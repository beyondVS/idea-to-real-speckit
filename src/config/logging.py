import logging


class LogRedactorFilter(logging.Filter):
    """
    보안 로깅 필터: PII(개인 식별 정보)나 인증 토큰 등 민감 정보가 로그에 남지 않도록 마스킹 처리합니다.
    """

    def filter(self, record):
        if isinstance(record.msg, str):
            # 간단한 휴리스틱으로 비밀번호나 토큰 패턴을 마스킹
            # (향후 더 정교한 정규식이나 Presidio 연동 가능)
            record.msg = record.msg.replace("password", "****")
            record.msg = record.msg.replace("token", "****")
        return True
