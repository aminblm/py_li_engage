from pathlib import Path
from typing import Final


class AppConstants:
    COOKIES_FILE_PATH: Final[Path] = Path(__file__).parent.parent.parent / "py_li_engage/data/linkedin-cookies.json"
    
    GROQ_API_URL: Final[str] = "https://api.groq.com/openai/v1/chat/completions"
    GROQ_MODEL_NAME: Final[str] = "llama-3.3-70b-versatile"
    
    LOGIN_URL: Final[str] = "https://www.linkedin.com/login"
    POST_LOGIN_INDICATOR_URL: Final[str] = "https://www.linkedin.com/feed/"

    DEFAULT_LOGIN_NAVIGATION_TIMEOUT_MS: Final[int] = 60000
    DEFAULT_VIEWPORT_SETTING: Final[bool] = True
    BROWSER_HEADLESS_MODE: Final[bool] = False
    
    PAGE_LOAD_WAIT_MS: Final[int] = 30000
    PROTOCOL_TIMEOUT_MS: Final[int] = 120000

    HUMAN_TYPING_MIN_MS: Final[int] = 60
    HUMAN_TYPING_MAX_MS: Final[int] = 160
    HUMAN_DELAY_VARIANCE: Final[float] = 0.35
    
    SLEEP_SHORT_MS: Final[int] = 2500
    SLEEP_LIKE_MS: Final[int] = 1000
    SLEEP_INSERT_MS: Final[int] = 1000
    SLEEP_PUBLISH_MS: Final[int] = 3000
    SLEEP_MODAL_MS: Final[int] = 3000
    SLEEP_CONTEXT_MS: Final[int] = 2500
    
    MACRO_BREAK_MIN_MS: Final[int] = 15000
    MACRO_BREAK_MAX_MS: Final[int] = 35000
    
    SCROLL_STEP_MIN_PX: Final[int] = 100
    SCROLL_STEP_MAX_PX: Final[int] = 350
    SCROLL_PAUSE_MIN_MS: Final[int] = 150
    SCROLL_PAUSE_MAX_MS: Final[int] = 450

    DOM_CONTENT_LOADED_STR: Final[str] = "domcontentloaded"
    FEED_ROUTE_PATH: Final[str] = "/feed"
    JSON_INDENT_SPACES: Final[int] = 2
    UTF8_ENCODING: Final[str] = "utf-8"
    LOGGER_NAME: Final[str] = "LinkedInAutomation"
    LOG_DATE_FORMAT: Final[str] = "%Y-%m-%dT%H:%M:%SZ"

    SELECTORS: Final[dict[str, str]] = {
        "SHARE_BUTTON": 'button[aria-label*="Share" i], a[aria-label*="Share" i], button[aria-label*="Send" i], a[aria-label*="Send" i], [class*="share-button"], [class*="social-share"]',
        "COPY_LINK_CANDIDATE": 'button, div[role="button"], a, span, li',
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