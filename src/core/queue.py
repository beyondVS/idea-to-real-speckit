import asyncio
import logging
from collections.abc import Callable, Coroutine
from typing import Any

logger = logging.getLogger(__name__)


class TaskQueue:
    """
    asyncio.Queue를 사용한 간단한 로컬 작업 큐입니다.
    Ollama 서버 부하 방지를 위해 요청을 순차적으로 처리합니다.
    """

    def __init__(self) -> None:
        self.queue: asyncio.Queue | None = None
        self.worker_task: asyncio.Task | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

    async def _worker(self) -> None:
        """
        큐에서 작업을 하나씩 꺼내어 처리하는 워커입니다.
        """
        if self.queue is None:
            return

        while True:
            try:
                func, args, kwargs, future = await self.queue.get()
                try:
                    result = await func(*args, **kwargs)
                    if not future.done():
                        future.set_result(result)
                except Exception as e:
                    logger.error(f"TaskQueue worker task execution error: {e}")
                    if not future.done():
                        future.set_exception(e)
                finally:
                    self.queue.task_done()
            except RuntimeError as e:
                # 루프 충돌 발생 시 워커 종료 (외부에서 다시 시작 유도)
                logger.warning(f"TaskQueue worker loop mismatch detected: {e}")
                break
            except Exception as e:
                logger.error(f"TaskQueue worker unexpected error: {e}")
                break

    def start(self) -> None:
        """
        워커를 시작합니다. 큐가 없거나 루프가 바뀌었으면 현재 루프에서 재설정합니다.
        """
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            return # 루프가 실행 중이 아니면 시작 불가

        # 1. 큐 초기화 또는 루프 변경 감지 시 재설정
        if self.queue is None or self._loop != current_loop:
            self.queue = asyncio.Queue()
            self._loop = current_loop
            self.worker_task = None
            logger.info(f"TaskQueue (re)initialized for loop: {id(current_loop)}")
            
        # 2. 워커 태스크가 없거나 종료된 경우 시작
        if self.worker_task is None or self.worker_task.done():
            self.worker_task = asyncio.create_task(self._worker())
            logger.info("TaskQueue worker started.")

    async def enqueue(
        self, func: Callable[..., Coroutine[Any, Any, Any]], *args: Any, **kwargs: Any
    ) -> Any:
        """
        작업을 큐에 추가하고 결과를 기다립니다.
        """
        self.start()  # 워커 및 큐 상태 확인
        
        future = self._loop.create_future()
        await self.queue.put((func, args, kwargs, future))
        return await future


# 싱글톤 인스턴스
llm_queue = TaskQueue()
