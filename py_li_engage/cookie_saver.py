import asyncio
import json
import sys
from pathlib import Path
from typing import Final, Protocol
from playwright.async_api import Browser, BrowserContext, Page, Playwright
from playwright.async_api._context_manager import PlaywrightContextManager

from py_li_engage.config import logger
from py_li_engage.constants.log_messages import LogMessages
from py_li_engage.constants.app_constants import AppConstants


class BrowserInitializerProtocol(Protocol):
    async def initialize(self, p: Playwright) -> tuple[Browser, BrowserContext, Page]: ...


class LoginAuthenticatorProtocol(Protocol):
    async def wait_for_login(self, page: Page) -> None: ...


class CookieStorageProtocol(Protocol):
    def persist(self, cookies: list[dict]) -> None: ...


class PlaywrightBrowserInitializer:
    def __init__(self, headless_mode: bool, viewport_setting: bool) -> None:
        self._headless_mode: Final[bool] = headless_mode
        self._viewport_setting: Final[bool] = viewport_setting

    async def initialize(self, p: Playwright) -> tuple[Browser, BrowserContext, Page]:
        browser: Browser = await p.chromium.launch(headless=self._headless_mode)
        context: BrowserContext = await browser.new_context(no_viewport=self._viewport_setting)
        page: Page = await context.new_page()
        return browser, context, page


class LinkedInLoginAuthenticator:
    def __init__(self, login_url: str, post_login_indicator: str, feed_route: str, wait_until: str, timeout_ms: int) -> None:
        self._login_url: Final[str] = login_url
        self._post_login_indicator: Final[str] = post_login_indicator
        self._feed_route: Final[str] = feed_route
        self._wait_until: Final[str] = wait_until
        self._timeout_ms: Final[int] = timeout_ms

    async def wait_for_login(self, page: Page) -> None:
        logger.info(LogMessages.NAVIGATING_LOGIN_INFO.format(self._login_url))
        await page.goto(self._login_url, wait_until=self._wait_until)
        
        logger.info(LogMessages.MANUAL_LOGIN_PROMPT_INFO)
        try:
            await page.wait_for_url(
                lambda url: self._feed_route in url or url.startswith(self._post_login_indicator),
                timeout=self._timeout_ms
            )
            logger.info(LogMessages.LOGIN_REDIRECT_SUCCESS_INFO)
        except Exception:
            logger.warning(LogMessages.LOGIN_REDIRECT_TIMEOUT_WARNING)


class JsonCookieStorage:
    def __init__(self, cookie_file: Path, json_indent: int, encoding: str) -> None:
        self._cookie_file: Final[Path] = cookie_file
        self._json_indent: Final[int] = json_indent
        self._encoding: Final[str] = encoding

    def persist(self, cookies: list[dict]) -> None:
        self._cookie_file.parent.mkdir(parents=True, exist_ok=True)
        serialized_cookies: str = json.dumps(cookies, indent=self._json_indent)
        self._cookie_file.write_text(serialized_cookies, encoding=self._encoding)
        logger.info(LogMessages.COOKIES_SAVED_SUCCESS_INFO.format(self._cookie_file.resolve()))


class CookieSaver:
    def __init__(
        self,
        playwright_context_manager: PlaywrightContextManager,
        browser_initializer: BrowserInitializerProtocol,
        authenticator: LoginAuthenticatorProtocol,
        storage: CookieStorageProtocol,
    ) -> None:
        self._playwright_cm: Final[PlaywrightContextManager] = playwright_context_manager
        self._browser_initializer: Final[BrowserInitializerProtocol] = browser_initializer
        self._authenticator: Final[LoginAuthenticatorProtocol] = authenticator
        self._storage: Final[CookieStorageProtocol] = storage

    async def save(self) -> bool:
        browser: Browser | None = None
        context: BrowserContext | None = None
        page: Page | None = None
        try:
            async with self._playwright_cm as p:
                browser, context, page = await self._browser_initializer.initialize(p)
                await self._authenticator.wait_for_login(page)

                cookies: list[dict] = await context.cookies()
                if not cookies:
                    logger.error(LogMessages.COOKIES_NOT_FOUND_ERROR)
                    return False

                self._storage.persist(cookies)
                return True

        except Exception as error:
            logger.critical(LogMessages.SAVE_ERROR_CRITICAL.format(error))
            return False
            
        finally:
            if browser:
                await browser.close()


def main() -> None:
    from playwright.async_api import async_playwright

    browser_init = PlaywrightBrowserInitializer(
        headless_mode=AppConstants.BROWSER_HEADLESS_MODE,
        viewport_setting=AppConstants.DEFAULT_VIEWPORT_SETTING
    )
    
    authenticator = LinkedInLoginAuthenticator(
        login_url=AppConstants.LOGIN_URL,
        post_login_indicator=AppConstants.POST_LOGIN_INDICATOR_URL,
        feed_route=AppConstants.FEED_ROUTE_PATH,
        wait_until=AppConstants.DOM_CONTENT_LOADED_STR,
        timeout_ms=AppConstants.DEFAULT_LOGIN_NAVIGATION_TIMEOUT_MS
    )
    
    storage = JsonCookieStorage(
        cookie_file=AppConstants.COOKIES_FILE_PATH,
        json_indent=AppConstants.JSON_INDENT_SPACES,
        encoding=AppConstants.UTF8_ENCODING
    )

    saver = CookieSaver(
        playwright_context_manager=async_playwright(),
        browser_initializer=browser_init,
        authenticator=authenticator,
        storage=storage,
    )
    
    success: bool = asyncio.run(saver.save())
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()