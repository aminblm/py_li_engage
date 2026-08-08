import logging
from typing import Final
from colorama import Fore, Style, init

from py_li_engage.constants.app_constants import AppConstants

init(autoreset=True)

class ColorFormatter(logging.Formatter):
    COLORS: Final[dict[int, str]] = {
        logging.DEBUG: Style.DIM + Fore.BLUE,
        logging.INFO: Fore.CYAN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Style.BRIGHT + Fore.RED,
    }

    def format(self, record: logging.LogRecord) -> str:
        color: str = self.COLORS.get(record.levelno, Fore.WHITE)
        timestamp: str = self.formatTime(record, self.datefmt)
        return f"{Style.DIM}[{timestamp}]{Style.RESET_ALL} {color}[{record.levelname}]{Style.RESET_ALL} {record.getMessage()}"


class LoggingConfigurator:
    @staticmethod
    def configure_logger(name: str, level: int = logging.INFO, date_format: str = AppConstants.LOG_DATE_FORMAT) -> logging.Logger:
        handler: logging.StreamHandler = logging.StreamHandler()
        handler.setFormatter(ColorFormatter(datefmt=date_format))

        logger: logging.Logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.handlers.clear()
        logger.addHandler(handler)
        return logger
    

logger: Final[logging.Logger] = LoggingConfigurator.configure_logger(AppConstants.LOGGER_NAME)
