from typing import Final


class LogMessages:
    NAVIGATING_LOGIN_INFO: Final[str] = "Navigating to login portal: {}"
    MANUAL_LOGIN_PROMPT_INFO: Final[str] = "Please log in manually (including completing any 2FA/CAPTCHA)..."
    LOGIN_REDIRECT_SUCCESS_INFO: Final[str] = "Login detected successfully via route redirection."
    LOGIN_REDIRECT_TIMEOUT_WARNING: Final[str] = "Timeout reached waiting for automatic redirect. Checking cookie presence..."
    COOKIES_NOT_FOUND_ERROR: Final[str] = "No cookies found in the browser context. Authentication failed."
    COOKIES_SAVED_SUCCESS_INFO: Final[str] = "Cookies successfully persisted to {}"
    SAVE_ERROR_CRITICAL: Final[str] = "Critical execution error while saving cookies: {}"

    # Services & Automation Log Messages
    COMMENT_SERVICE_LOG_PREFIX: Final[str] = "[COMMENT_SERVICE] "
    CLEANING_COMMENT_INFO: Final[str] = "Cleaning generated comment text."
    GROQ_SERVICE_LOG_PREFIX: Final[str] = "[GROQ_SERVICE] "
    GROQ_API_REQUEST_INFO: Final[str] = "Initiating request to Groq API for comment generation."
    GROQ_API_SUCCESS_INFO: Final[str] = "Groq comment generation successful."
    GROQ_API_ERROR_ERROR: Final[str] = "Error communicating with Groq API: {}"

    SESSION_MANAGER_LOG_PREFIX: Final[str] = "[SESSION_MANAGER] "
    BROWSER_INIT_INFO: Final[str] = "Initializing Playwright browser session."
    COOKIES_INJECTED_SUCCESS_INFO: Final[str] = "Cookies injected successfully."
    BROWSER_INIT_SUCCESS_INFO: Final[str] = "Browser session initialized successfully."
    BROWSER_INIT_FAILED_ERROR: Final[str] = "Failed to load configuration or initialize browser session: {}"

    HUMANIZATION_LOG_PREFIX: Final[str] = "[HUMANIZATION] "
    HUMAN_MICRO_BREAK_INFO: Final[str] = "Taking a natural human micro-break for {:.1f} seconds..."
    HUMAN_DWELL_TIME_INFO: Final[str] = "Simulating reading dwell time for {:.1f} seconds based on post length."
    HUMAN_SCROLL_ELEMENT_INFO: Final[str] = "Scrolling organically to element: {}"
    HUMAN_SCROLL_SCAN_INFO: Final[str] = "Performing organic scroll-and-scan behavior on page load..."
    HUMAN_SCROLL_SCAN_WARN: Final[str] = "Non-critical error during page scroll scan: {}"
    HUMAN_TYPE_INFO: Final[str] = "Typing text organically into selector: {}"