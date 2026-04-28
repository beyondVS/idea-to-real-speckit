import json
import logging
from typing import Any, Dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from psycopg import AsyncConnection
from apps.inquiry.models import InquirySession
from apps.inquiry.graph import get_compiled_graph
from apps.inquiry.services import generate_problem_specification

logger = logging.getLogger(__name__)

@csrf_exempt
async def chat_api(request) -> JsonResponse:
    """
    진단 엔진과 대화하는 비동기 API 엔드포인트.
    
    사용자의 입력을 받아 LangGraph 상태 머신을 구동하고,
    분석 결과 또는 다음 질문을 반환합니다.
    
    Args:
        request: HttpRequest 객체 (session_id, user_input 포함)
        
    Returns:
        JsonResponse: AI 응답 및 대화 상태 데이터
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
        
    session_id = data.get("session_id")
    user_input = data.get("user_input", "")
    
    if not user_input.strip():
        return JsonResponse({"error": "질문을 입력해주세요."}, status=400)
    
    # 1. 세션 확인 및 생성
    if not session_id:
        session = await InquirySession.objects.acreate()
        session_id = str(session.id)
    else:
        try:
            session = await InquirySession.objects.aget(id=session_id)
        except InquirySession.DoesNotExist:
            return JsonResponse({"error": "존재하지 않는 세션입니다."}, status=404)

    if session.is_completed:
         return JsonResponse({"error": "이미 완료된 진단 세션입니다."}, status=400)

    # 2. DB 연결 및 엔진 구동
    try:
        # Django DB 설정을 바탕으로 psycopg 비동기 연결 획득
        db_config = settings.DATABASES['default']
        conn_str = f"dbname={db_config['NAME']} user={db_config['USER']} password={db_config['PASSWORD']} host={db_config['HOST']} port={db_config['PORT']}"
        
        async with await AsyncConnection.connect(conn_str) as conn:
            app = get_compiled_graph(conn)
            
            # 대화 기록 구성
            config = {"configurable": {"thread_id": session_id}}
            
            # 입력 상태 준비
            input_state = {
                "messages": [{"role": "user", "content": user_input}]
            }
            
            # 엔진 실행 (T020 반영)
            final_state = await app.ainvoke(input_state, config=config)
            
            last_message = final_state["messages"][-1]
            current_step = final_state.get("current_step", 1)
            
            # 종료 제안 여부 확인 (US3 관련)
            show_agreement = (current_step > 5)
            
            return JsonResponse({
                "status": "success",
                "data": {
                    "session_id": session_id,
                    "ai_response": last_message["content"],
                    "current_step": current_step,
                    "is_completed": session.is_completed,
                    "show_agreement": show_agreement
                }
            })
            
    except Exception as e:
        logger.exception(f"채팅 API 처리 중 치명적 오류 발생: {e}")
        return JsonResponse({"error": "AI 엔진 서버 통신 중 오류가 발생했습니다."}, status=500)

@csrf_exempt
async def confirm_completion_api(request) -> JsonResponse:
    """
    사용자의 종료 동의를 처리하고 기술서를 생성합니다.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
        
    data = json.loads(request.body)
    session_id = data.get("session_id")
    
    try:
        db_config = settings.DATABASES['default']
        conn_str = f"dbname={db_config['NAME']} user={db_config['USER']} password={db_config['PASSWORD']} host={db_config['HOST']} port={db_config['PORT']}"
        
        async with await AsyncConnection.connect(conn_str) as conn:
            app = get_compiled_graph(conn)
            config = {"configurable": {"thread_id": session_id}}
            state = await app.aget_state(config)
            
            # 기술서 생성 (T024)
            spec = await generate_problem_specification(session_id, state.values)
            
            return JsonResponse({
                "status": "success",
                "data": {
                    "markdown": spec.content_markdown,
                    "json": spec.content_json
                }
            })
    except Exception as e:
        logger.exception(f"기술서 생성 실패: {e}")
        return JsonResponse({"error": "기술서 생성 중 오류가 발생했습니다."}, status=500)
