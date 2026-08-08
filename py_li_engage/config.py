import json
import logging
from pathlib import Path
from typing import Final, Dict, List
from colorama import Fore, Style, init

from py_li_engage.constants.app_constants import AppConstants
from py_li_engage.constants.log_messages import LogMessages
init(autoreset=True)


class ColorFormatter(logging.Formatter):
    COLORS: Final[Dict[int, str]] = {
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


class FileReader:
    @staticmethod
    def read_json(file_path: Path) -> dict | list:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        return json.loads(file_path.read_text(encoding=AppConstants.UTF8_ENCODING))


logger: Final[logging.Logger] = LoggingConfigurator.configure_logger(AppConstants.LOGGER_NAME)


class ConfigLoader:
    def __init__(self, root_path: Path, config_file_path: Path, profiles_file_path: Path) -> None:
        self._root_path: Path = root_path
        self._config_file_path: Path = config_file_path
        self._profiles_file_path: Path = profiles_file_path

    def load_api_key(self) -> str:
        logger.info(LogMessages.CONFIG_LOADING_INFO)
        try:
            full_path: Path = self._root_path / self._config_file_path
            config_data = FileReader.read_json(full_path)
            
            if not isinstance(config_data, dict) or not config_data.get("GROQ_API_KEY"):
                raise ValueError("GROQ_API_KEY is missing from config file.")
            
            logger.info(LogMessages.CONFIG_LOADED_SUCCESS_INFO)
            api_key: str = config_data["GROQ_API_KEY"]
            return api_key
        except Exception as error:
            logger.error(LogMessages.CONFIG_LOAD_FAILED_ERROR.format(error))
            raise

    def load_target_urls(self) -> List[str]:
        logger.info(LogMessages.PROFILES_LOADING_INFO)
        try:
            full_path: Path = self._root_path / self._profiles_file_path
            urls = FileReader.read_json(full_path)
            
            if not isinstance(urls, list) or len(urls) == 0:
                raise ValueError("Profiles JSON must contain a non-empty array of URLs.")
            
            logger.info(LogMessages.PROFILES_LOADED_SUCCESS_INFO.format(len(urls)))
            return urls
        except Exception as error:
            logger.error(LogMessages.PROFILES_LOAD_FAILED_ERROR.format(error))
            raise