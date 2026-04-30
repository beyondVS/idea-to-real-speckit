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
    진행 중인 세션 목록을 보여주는 대시보드 뷰입니다. (T027)
    """
    # 데모용: User ID 1의 세션 목록 조회
    sessions = InquirySession.objects.filter(user_id=1).order_by("-updated_at")
    return render(request, "inquiry/dashboard.html", {"sessions": sessions})


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
                app = get_compiled_graph(conn)
                config = {"configurable": {"thread_id": session_id}}
                input_state = {
                    "initial_input": initial_input,
                    "messages": [{"role": "user", "content": initial_input}],
                    "current_step": 0,
                }
                return await app.ainvoke(input_state, config=config)

        # 큐에 작업 등록 및 결과 대기
        final_state = await llm_queue.enqueue(run_engine)

        return JsonResponse(
            {
                "session_id": session_id,
                "status": "in_progress",
                "question": final_state["messages"][-1]["content"],
                "step": final_state["current_step"],
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

        async def run_engine():
            async with await AsyncConnection.connect(conn_str) as conn:
                app = get_compiled_graph(conn)
                config = {"configurable": {"thread_id": session_id}}
                input_state = {"messages": [{"role": "user", "content": answer}]}
                return await app.ainvoke(input_state, config=config)

        # 큐에 작업 등록 및 결과 대기
        final_state = await llm_queue.enqueue(run_engine)

        return JsonResponse(
            {
                "status": "in_progress",
                "question": final_state["messages"][-1]["content"],
                "step": final_state["current_step"],
                "is_final_diagnosis": final_state.get("is_final_diagnosis", False),
                "awaiting_consent": final_state.get("awaiting_consent", False),
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
            app = get_compiled_graph(conn)
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
            app = get_compiled_graph(conn)
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
