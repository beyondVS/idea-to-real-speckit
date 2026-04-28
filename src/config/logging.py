import logging
import re

class LogRedactorFilter(logging.Filter):
    """
    민감 정보(이메일, 전화번호 등)를 마스킹하기 위한 로깅 필터.
    """
    
    EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    PHONE_PATTERN = re.compile(r'\b010[-.]?\d{4}[-.]?\d{4}\b')
    
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.EMAIL_PATTERN.sub('***@***.***', record.msg)
            record.msg = self.PHONE_PATTERN.sub('010-****-****', record.msg)
        return True
