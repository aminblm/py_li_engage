from typing import Final

class LogMessages:
    NAVIGATING_LOGIN_INFO: Final[str] = "Navigating to login portal: {}"
    MANUAL_LOGIN_PROMPT_INFO: Final[str] = "Please log in manually (including completing any 2FA/CAPTCHA)..."
    LOGIN_REDIRECT_SUCCESS_INFO: Final[str] = "Login detected successfully via route redirection."
    LOGIN_REDIRECT_TIMEOUT_WARNING: Final[str] = "Timeout reached waiting for automatic redirect. Checking cookie presence..."
    COOKIES_NOT_FOUND_ERROR: Final[str] = "No cookies found in the browser context. Authentication failed."
    COOKIES_SAVED_SUCCESS_INFO: Final[str] = "Cookies successfully persisted to {}"
    SAVE_ERROR_CRITICAL: Final[str] = "Critical execution error while saving cookies: {}"

    CONFIG_LOADING_INFO: Final[str] = "Loading configuration file..."
    CONFIG_LOADED_SUCCESS_INFO: Final[str] = "Configuration loaded successfully."
    CONFIG_LOAD_FAILED_ERROR: Final[str] = "Failed to load configuration: {}"
    PROFILES_LOADING_INFO: Final[str] = "Loading profile targets from json file..."
    PROFILES_LOADED_SUCCESS_INFO: Final[str] = "Loaded {0} target URLs from profiles file."
    PROFILES_LOAD_FAILED_ERROR: Final[str] = "Failed to load profile targets: {}"