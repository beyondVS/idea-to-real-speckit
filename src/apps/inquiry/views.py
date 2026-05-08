import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from psycopg import AsyncConnection

from apps.inquiry.graph import get_compiled_graph
from apps.inquiry.models import InquirySession
from apps.inquiry.services import generate_problem_specification, save_user_rating
from core.queue import llm_queue

logger = logging.getLogger(__name__)


async def dashboard_view(request):
    """
    진행 중인 세션 목록을 보여주는 대시보드 뷰입니다.
    """
    # 비동기 리스트 컴프리헨션을 사용하여 비동기적으로 데이터를 가져옵니다.
    queryset = InquirySession.objects.filter(user_id=1).order_by("-updated_at")
    sessions = [session async for session in queryset]
    return render(request, "inquiry/dashboard.html", {"sessions": sessions})


@csrf_exempt
async def get_history_api(request, session_id: str) -> JsonResponse:
    """
    GET /api/inquiry/<session_id>/history/
    기존 세션의 대화 이력을 반환합니다. (LangGraph 체크포인트 활용)
    """
    try:
        db_config = settings.DATABASES["default"]
        conn_str = (
            f"dbname={db_config['NAME']} "
            f"user={db_config['USER']} "
            f"password={db_config['PASSWORD']} "
            f"host={db_config['HOST']} "
            f"port={db_config['PORT']}"
        )

        async with await AsyncConnection.connect(conn_str) as conn:
            app = await get_compiled_graph(conn)
            config = {"configurable": {"thread_id": session_id}}
            state = await app.aget_state(config)

            if not state.values:
                return JsonResponse({"messages": [], "step": 0})

            # LangGraph State에서 메시지 목록 추출
            messages = []
            for m in state.values.get("messages", []):
                # 1. 콘텐츠 추출
                if hasattr(m, "content"):
                    content = m.content
                elif isinstance(m, dict):
                    content = m.get("content", "")
                else:
                    content = str(m)

                # 2. 역할(Role) 판단
                is_ai = False
                if hasattr(m, "type"):
                    is_ai = m.type == "ai"
                elif isinstance(m, dict):
                    is_ai = m.get("role") == "assistant"

                role = "assistant" if is_ai else "user"
                messages.append({"role": role, "content": content})


            return JsonResponse(
                {
                    "messages": messages,
                    "turn_count": state.values.get("turn_count", 0),
                    "invalid_response_count": state.values.get(
                        "invalid_response_count", 0
                    ),
                    "root_cause": state.values.get("root_cause"),
                    "is_extension_approved": state.values.get(
                        "is_extension_approved", False
                    ),
                }
            )
    except Exception as e:
        logger.exception("이력 조회 오류: %s", e)
        return JsonResponse(
            {"error": "이력을 불러오는 중 오류가 발생했습니다."}, status=500
        )


@csrf_exempt
async def start_session_api(request) -> JsonResponse:
    """
    POST /api/inquiry/start/
    새로운 진단 세션을 생성하고 작업 큐를 통해 최초 질문을 생성합니다.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        initial_input = data.get("initial_input", "")

        if not initial_input.strip():
            return JsonResponse({"error": "초기 입력을 제공해주세요."}, status=400)

        # 1. 세션 생성 (데모용 고정 User ID 1)
        session = await InquirySession.objects.acreate(user_id=1)
        session_id = str(session.id)

        # 2. 엔진 구동 (작업 큐 활용)
        db_config = settings.DATABASES["default"]
        conn_str = (
            f"dbname={db_config['NAME']} "
            f"user={db_config['USER']} "
            f"password={db_config['PASSWORD']} "
            f"host={db_config['HOST']} "
            f"port={db_config['PORT']}"
        )

        async def run_engine():
            async with await AsyncConnection.connect(conn_str) as conn:
                app = await get_compiled_graph(conn)
                config = {"configurable": {"thread_id": session_id}}
                # 초기 상태 설정 (InquiryState 스키마 준수)
                input_state = {
                    "messages": [{"role": "user", "content": initial_input}],
                    "turn_count": 0,
                    "invalid_response_count": 0,
                    "is_extension_approved": False,
                    "root_cause": None,
                    "metadata": {},
                }
                return await app.ainvoke(input_state, config=config)

        # 큐에 작업 등록 및 결과 대기
        final_state = await llm_queue.enqueue(run_engine)

        return JsonResponse(
            {
                "session_id": session_id,
                "status": "IN_PROGRESS",
                "question": final_state["messages"][-1].content,
                "turn_count": final_state["turn_count"],
            },
            status=201,
        )

    except Exception as e:
        logger.exception("세션 시작 실패: %s", e)
        return JsonResponse({"error": "서버 통신 중 오류가 발생했습니다."}, status=500)


@csrf_exempt
async def chat_api(request, session_id: str) -> JsonResponse:
    """
    POST /api/inquiry/<session_id>/chat/
    사용자의 답변을 전송하고 작업 큐를 통해 다음 단계의 질문을 생성합니다.
    연장 승인 처리 로직을 포함합니다.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        answer = data.get("answer", "")

        if not answer.strip():
            return JsonResponse({"error": "답변을 입력해주세요."}, status=400)

        db_config = settings.DATABASES["default"]
        conn_str = (
            f"dbname={db_config['NAME']} "
            f"user={db_config['USER']} "
            f"password={db_config['PASSWORD']} "
            f"host={db_config['HOST']} "
            f"port={db_config['PORT']}"
        )

        # 연장 승인 여부 판단 (특정 키워드 또는 플래그 활용)
        is_extension_approval = answer == "질의를 연장하겠습니다."

        async def run_engine():
            async with await AsyncConnection.connect(conn_str) as conn:
                app = await get_compiled_graph(conn)
                config = {"configurable": {"thread_id": session_id}}

                input_state = {"messages": [{"role": "user", "content": answer}]}
                if is_extension_approval:
                    logger.info("Extension approved for session %s", session_id)
                    input_state["is_extension_approved"] = True

                return await app.ainvoke(input_state, config=config)

        # 큐에 작업 등록 및 결과 대기
        final_state = await llm_queue.enqueue(run_engine)

        # 마지막 메시지 추출
        last_msg = final_state["messages"][-1]
        question = (
            last_msg.content
            if hasattr(last_msg, "content")
            else last_msg.get("content", "")
        )

        return JsonResponse(
            {
                "status": "IN_PROGRESS",
                "question": question,
                "turn_count": final_state["turn_count"],
                "invalid_response_count": final_state.get("invalid_response_count", 0),
                "root_cause": final_state.get("root_cause"),
                "is_extension_approved": final_state.get(
                    "is_extension_approved", False
                ),
            }
        )

    except Exception as e:
        logger.exception("채팅 오류: %s", e)
        return JsonResponse(
            {"error": "엔진 서버 통신 중 오류가 발생했습니다."}, status=500
        )


@csrf_exempt
async def rollback_api(request, session_id: str) -> JsonResponse:
    """
    POST /api/inquiry/<session_id>/rollback/
    이전 단계로 대화 상태를 되돌립니다. (T025)
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body)
        target_step = data.get("target_step")
        if target_step is None:
            return JsonResponse({"error": "대상 단계를 지정해주세요."}, status=400)

        db_config = settings.DATABASES["default"]
        conn_str = (
            f"dbname={db_config['NAME']} "
            f"user={db_config['USER']} "
            f"password={db_config['PASSWORD']} "
            f"host={db_config['HOST']} "
            f"port={db_config['PORT']}"
        )

        async with await AsyncConnection.connect(conn_str) as conn:
            app = await get_compiled_graph(conn)
            config = {"configurable": {"thread_id": session_id}}

            # 히스토리에서 해당 단계 찾기
            state = await app.aget_state(config)
            new_values = state.values.copy()
            new_values["current_step"] = target_step

            await app.aupdate_state(config, new_values)

            return JsonResponse(
                {
                    "current_step": target_step,
                    "last_question": "롤백되었습니다. 다시 답변해 주세요.",
                }
            )
    except Exception as e:
        logger.exception("롤백 오류: %s", e)
        return JsonResponse({"error": "상태 복구 중 오류가 발생했습니다."}, status=500)


@csrf_exempt
async def rate_session_api(request, session_id: str) -> JsonResponse:
    """
    POST /api/inquiry/<session_id>/rate/
    사용자 만족도 점수를 저장합니다.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body)
        rating = data.get("rating")
        if rating is None or not (1 <= rating <= 5):
            return JsonResponse(
                {"error": "올바른 점수(1-5)를 입력해주세요."}, status=400
            )

        success = await save_user_rating(session_id, rating)
        if success:
            return JsonResponse(
                {"status": "success", "message": "만족도 조사가 완료되었습니다."}
            )
        else:
            return JsonResponse({"error": "점수 저장에 실패했습니다."}, status=404)
    except Exception as e:
        logger.exception("만족도 저장 오류: %s", e)
        return JsonResponse({"error": "서버 내부 오류가 발생했습니다."}, status=500)


@csrf_exempt
async def confirm_completion_api(request, session_id: str) -> JsonResponse:
    """
    POST /api/inquiry/<session_id>/confirm/
    종료 동의 시 보고서를 생성합니다.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        db_config = settings.DATABASES["default"]
        conn_str = (
            f"dbname={db_config['NAME']} "
            f"user={db_config['USER']} "
            f"password={db_config['PASSWORD']} "
            f"host={db_config['HOST']} "
            f"port={db_config['PORT']}"
        )
        async with await AsyncConnection.connect(conn_str) as conn:
            app = await get_compiled_graph(conn)
            config = {"configurable": {"thread_id": session_id}}
            state = await app.aget_state(config)
            spec = await generate_problem_specification(session_id, state.values)
            return JsonResponse(
                {
                    "status": "success",
                    "data": {"markdown": spec.content_md, "json": spec.content_json},
                }
            )
    except Exception as e:
        logger.exception("기술서 생성 실패: %s", e)
        return JsonResponse(
            {"error": "기술서 생성 중 오류가 발생했습니다."}, status=500
        )
