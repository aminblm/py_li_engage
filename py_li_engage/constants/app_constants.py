from pathlib import Path
from typing import Final


class AppConstants:
    COOKIES_FILE_PATH: Final[Path] = Path(__file__).parent.parent.parent / "py_li_engage/data/linkedin-cookies.json"
    
    GROQ_API_URL: Final[str] = "https://api.groq.com/openai/v1/chat/completions"
    GROQ_MODEL_NAME: Final[str] = "llama-3.3-70b-versatile"

    GROQ_REQUEST_TIMEOUT_SEC: Final[float] = 30.0
    GROQ_ROLE_USER: Final[str] = "user"
    GROQ_CHOICES_KEY: Final[str] = "choices"
    GROQ_MESSAGE_KEY: Final[str] = "message"
    GROQ_CONTENT_KEY: Final[str] = "content"
    GROQ_COMMENT_PROMPT_TEMPLATE: Final[str] = (
        'Write the shortest and most engaging professional comment for this LinkedIn post content: "{post_content}". '
        "Do NOT include any emojis whatsoever."
    )
    
    LOGIN_URL: Final[str] = "https://www.linkedin.com/login"
    POST_LOGIN_INDICATOR_URL: Final[str] = "https://www.linkedin.com/feed/"

    DEFAULT_LOGIN_NAVIGATION_TIMEOUT_MS: Final[int] = 60000
    DEFAULT_VIEWPORT_SETTING: Final[bool] = True
    BROWSER_HEADLESS_MODE: Final[bool] = False
    
    PAGE_LOAD_WAIT_MS: Final[int] = 30000
    PROTOCOL_TIMEOUT_MS: Final[int] = 120000

    DEFAULT_NAVIGATION_TIMEOUT_MS: Final[int] = 60000
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

    COMMAND_LINE_MAXIMIZED_ARG: Final[str] = "--start-maximized"
    COMMENT_CLEAN_REGEX_UNICODE: Final[str] = r"[\U0001f000-\U0001f6ff\U0001f900-\U0001f9ff\u2600-\u27bf]"
    QUOTE_STRIP_PATTERN: Final[str] = r"^[\"\']+|[\"\']+$"
    DASH_SPACING_PATTERN: Final[str] = r"\s*-\s*"
    SCROLL_OFFSET_PX: Final[int] = 200
    SCROLL_DURATION_MIN_MS: Final[float] = 400.0
    SCROLL_DURATION_MAX_MS: Final[float] = 1500.0
    SCROLL_MULTIPLIER_FACTOR: Final[float] = 0.5
    STOCHASTIC_SLEEP_MS: Final[float] = 800.0
    POST_LOAD_SLEEP_MS: Final[float] = 1000.0
    READING_TIME_DIVISOR: Final[float] = 18.0
    READING_TIME_MIN_SEC: Final[float] = 3.0
    READ_JITTER_MIN_FACTOR: Final[float] = 0.8
    READ_JITTER_MAX_FACTOR: Final[float] = 1.2
    PUNCTUATION_DELAY_MIN_MS: Final[int] = 150
    PUNCTUATION_DELAY_MAX_MS: Final[int] = 450
    JS_EASE_OUT_QUAD_SNIPPET: Final[str] = "function easeOutQuad(t) { return t * (2 - t); }"

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