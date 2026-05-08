import asyncio

from django.conf import settings
from django.core.management.base import BaseCommand
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg import AsyncConnection


class Command(BaseCommand):
    help = "LangGraph 운영에 필요한 PostgreSQL 테이블 및 인덱스를 생성합니다."

    def handle(self, *args, **options):
        asyncio.run(self.setup_db())

    async def setup_db(self):
        db_config = settings.DATABASES["default"]
        conn_str = (
            f"dbname={db_config['NAME']} "
            f"user={db_config['USER']} "
            f"password={db_config['PASSWORD']} "
            f"host={db_config['HOST']} "
            f"port={db_config['PORT']}"
        )

        self.stdout.write(self.style.SUCCESS("데이터베이스에 연결 중..."))

        try:
            # autocommit=True로 설정하여 CREATE INDEX CONCURRENTLY 에러 방지
            async with await AsyncConnection.connect(conn_str, autocommit=True) as conn:
                checkpointer = AsyncPostgresSaver(conn)
                self.stdout.write("LangGraph 스키마 생성 중...")
                await checkpointer.setup()
                self.stdout.write(
                    self.style.SUCCESS("성공적으로 LangGraph 설정을 완료했습니다.")
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"설정 중 오류 발생: {e}"))
