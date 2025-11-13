import logging
import re


class FilterSecrets(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        # Скрываем JWT, пароли, токены
        msg = re.sub(r"[A-Za-z0-9+/=]{20,}", "[REDACTED]", msg)  # JWT
        msg = re.sub(
            r'password["\']?:\s*["\'][^"\']+["\']', "password: [REDACTED]", msg
        )
        record.msg = msg
        return True


def setup_logging():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    logger.handlers[0].addFilter(FilterSecrets())
