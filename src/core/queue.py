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
        self.queue: asyncio.Queue = asyncio.Queue()
        self.worker_task: asyncio.Task | None = None

    async def _worker(self) -> None:
        """
        큐에서 작업을 하나씩 꺼내어 처리하는 워커입니다.
        """
        while True:
            func, args, kwargs, future = await self.queue.get()
            try:
                result = await func(*args, **kwargs)
                future.set_result(result)
            except Exception as e:
                logger.error(f"TaskQueue worker error: {e}")
                future.set_exception(e)
            finally:
                self.queue.task_done()

    def start(self) -> None:
        """
        워커를 시작합니다.
        """
        if self.worker_task is None or self.worker_task.done():
            self.worker_task = asyncio.create_task(self._worker())
            logger.info("TaskQueue worker started.")

    async def enqueue(
        self, func: Callable[..., Coroutine[Any, Any, Any]], *args: Any, **kwargs: Any
    ) -> Any:
        """
        작업을 큐에 추가하고 결과를 기다립니다.
        """
        self.start()  # 워커가 실행 중인지 확인
        future = asyncio.get_running_loop().create_future()
        await self.queue.put((func, args, kwargs, future))
        return await future


# 싱글톤 인스턴스
llm_queue = TaskQueue()
