import json
import logging
from pathlib import Path
from typing import Final
from colorama import Fore, Style, init

init(autoreset=True)

class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Style.DIM + Fore.BLUE,
        logging.INFO: Fore.CYAN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Style.BRIGHT + Fore.RED,
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, Fore.WHITE)
        timestamp = self.formatTime(record, self.datefmt)
        return f"{Style.DIM}[{timestamp}]{Style.RESET_ALL} {color}[{record.levelname}]{Style.RESET_ALL} {record.getMessage()}"

handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter(datefmt="%Y-%m-%dT%H:%M:%SZ"))

logger = logging.getLogger("LinkedInAutomation")
logger.setLevel(logging.INFO)
logger.handlers.clear()
logger.addHandler(handler)

COOKIES_FILE_PATH: Final[Path] = Path(__file__).parent.parent / "data/linkedin-cookies.json"
DEFAULT_LOGIN_NAVIGATION_TIMEOUT_MS: Final[int] = 60000
DEFAULT_VIEWPORT_SETTING: Final[bool] = True
BROWSER_HEADLESS_MODE: Final[bool] = False
DOM_CONTENT_LOADED_STR: Final[str] = "domcontentloaded"
FEED_ROUTE_PATH: Final[str] = "/feed"
JSON_INDENT_SPACES: Final[int] = 2
UTF8_ENCODING: Final[str] = "utf-8"
LOGIN_URL: Final[str] = "https://www.linkedin.com/login"
POST_LOGIN_INDICATOR_URL: Final[str] = "https://www.linkedin.com/feed/"

CONFIG_FILE_PATH= "data/config.json"
PROFILES_FILE_PATH = "data/linkedin-profiles.json"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL_NAME = "llama-3.3-70b-versatile"

PAGE_LOAD_WAIT_MS = 30000
PROTOCOL_TIMEOUT_MS = 120000

HUMAN_TYPING_MIN_MS = 60
HUMAN_TYPING_MAX_MS = 160
HUMAN_DELAY_VARIANCE = 0.35
SLEEP_SHORT_MS = 2500
SLEEP_LIKE_MS = 1000
SLEEP_INSERT_MS = 1000
SLEEP_PUBLISH_MS = 3000
SLEEP_MODAL_MS = 3000
SLEEP_CONTEXT_MS = 2500
MACRO_BREAK_MIN_MS = 15000
MACRO_BREAK_MAX_MS = 35000
SCROLL_STEP_MIN_PX = 100
SCROLL_STEP_MAX_PX = 350
SCROLL_PAUSE_MIN_MS = 150
SCROLL_PAUSE_MAX_MS = 450

SELECTORS: dict[str, str] = {
    "SHARE_BUTTON": 'button[aria-label*="Share" i], a[aria-label*="Share" i], button[aria-label*="Send" i], a[aria-label*="Send" i], [class*="share-button"], [class*="social-share"]',
    "COPY_LINK_CANDIDATE": "button, div[role=\"button\"], a, span, li",
    "POST_URL_MODAL": 'div[role="dialog"] a[href*="http"], .artdeco-modal a[href*="http"], a[href*="/posts/"], a[href*="/status/"]',
    "COMMENTARY_CONTAINER": ".update-components-update-v2__commentary",
    "LIKE_BUTTON": 'button.social-actions-button.react-button__trigger[aria-label="React Like"]',
    "COMMENT_EDITOR_BOX": '.comments-comment-box__form .ql-editor, div[contenteditable="true"][aria-label*="Text editor" i]',
    "PROFILE_SWITCHER_BTN": ".content-admin-identity-toggle-button",
    "MODAL_ITEMS": ".artdeco-modal__content li",
    "SAVE_BUTTON": '.artdeco-modal__actionbar button.artdeco-button--primary, button[data-control-name="identity_selector_save"], .artdeco-modal__actionbar button',
    "REPOST_BTN_FIRST": ".social-reshare-button",
    "REPOST_ITEM_SECOND": 'svg[data-test-icon="repost-medium"]',
}


class ConfigLoader:

    @staticmethod
    def load_api_key() -> str:
        logger.info("Loading configuration file...")
        try:
            config_path = Path(__file__).parent.parent / CONFIG_FILE_PATH
            if not config_path.exists():
                raise FileNotFoundError(f"Config file not found: {config_path}")
            
            config_data = json.loads(config_path.read_text(encoding="utf-8"))
            if not config_data.get("GROQ_API_KEY"):
                raise ValueError("GROQ_API_KEY is missing from config file.")
            
            logger.info("Configuration loaded successfully.")
            return config_data["GROQ_API_KEY"]
        except Exception as error:
            logger.error(f"Failed to load configuration: {error}")
            raise

    @staticmethod
    def load_target_urls() -> list[str]:
        logger.info("Loading profile targets from json file...")
        try:
            profiles_path: Path = Path(__file__).parent.parent / PROFILES_FILE_PATH
            if not profiles_path.exists():
                raise FileNotFoundError(f"Profiles file not found at: {profiles_path}")
            
            urls: list[str] = json.loads(profiles_path.read_text(encoding="utf-8"))
            if not isinstance(urls, list) or len(urls) == 0:
                raise ValueError("Profiles JSON must contain a non-empty array of URLs.")
            
            logger.info(f"Loaded {len(urls)} target URLs from profiles file.")
            return urls
        except Exception as error:
            logger.error(f"Failed to load profile targets: {error}")
            raise