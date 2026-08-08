import asyncio
import json
import sys
from pathlib import Path
from playwright.async_api._context_manager import PlaywrightContextManager
from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright
from py_li_engage.config import (
    COOKIES_FILE_PATH,
    DEFAULT_LOGIN_NAVIGATION_TIMEOUT_MS,
    DEFAULT_VIEWPORT_SETTING,
    BROWSER_HEADLESS_MODE,
    DOM_CONTENT_LOADED_STR,
    FEED_ROUTE_PATH,
    JSON_INDENT_SPACES,
    UTF8_ENCODING,
    LOGIN_URL,
    POST_LOGIN_INDICATOR_URL,
    logger,
)
from py_li_engage.constants.log_messages import (
    NAVIGATING_LOGIN_INFO,
    MANUAL_LOGIN_PROMPT_INFO,
    LOGIN_REDIRECT_SUCCESS_INFO,
    LOGIN_REDIRECT_TIMEOUT_WARNING,
    COOKIES_NOT_FOUND_ERROR,
    COOKIES_SAVED_SUCCESS_INFO,
    SAVE_ERROR_CRITICAL,
)


class CookieSaver:
    def __init__(
        self,
        cookie_file: Path,
        playwright_context_manager: PlaywrightContextManager,
        login_url: str,
        post_login_indicator: str,
        headless_mode: bool,
        timeout_ms: int,
    ) -> None:
        self._cookie_file = cookie_file
        self._playwright_cm = playwright_context_manager
        self._login_url = login_url
        self._post_login_indicator = post_login_indicator
        self._headless_mode = headless_mode
        self._timeout_ms = timeout_ms

    async def _initialize_browser(self, p: Playwright) -> tuple[Browser, BrowserContext, Page]:
        browser = await p.chromium.launch(headless=self._headless_mode)
        context = await browser.new_context(no_viewport=DEFAULT_VIEWPORT_SETTING)
        page = await context.new_page()
        return browser, context, page

    async def _wait_for_login(self, page: Page) -> None:
        logger.info(NAVIGATING_LOGIN_INFO.format(self._login_url))
        await page.goto(self._login_url, wait_until=DOM_CONTENT_LOADED_STR)
        
        logger.info(MANUAL_LOGIN_PROMPT_INFO)
        try:
            await page.wait_for_url(
                lambda url: FEED_ROUTE_PATH in url or url.startswith(self._post_login_indicator),
                timeout=self._timeout_ms
            )
            logger.info(LOGIN_REDIRECT_SUCCESS_INFO)
        except Exception:
            logger.warning(LOGIN_REDIRECT_TIMEOUT_WARNING)

    def _persist_cookies(self, cookies: list) -> None:
        self._cookie_file.parent.mkdir(parents=True, exist_ok=True)
        serialized_cookies = json.dumps(cookies, indent=JSON_INDENT_SPACES)
        self._cookie_file.write_text(serialized_cookies, encoding=UTF8_ENCODING)
        logger.info(COOKIES_SAVED_SUCCESS_INFO.format(self._cookie_file.resolve()))

    async def save(self) -> bool:
        browser, context, page = None, None, None
        try:
            async with self._playwright_cm as p:
                browser, context, page = await self._initialize_browser(p)
                await self._wait_for_login(page)

                cookies = await context.cookies()
                if not cookies:
                    logger.error(COOKIES_NOT_FOUND_ERROR)
                    return False

                self._persist_cookies(cookies)
                return True

        except Exception as error:
            logger.critical(SAVE_ERROR_CRITICAL.format(error))
            return False
            
        finally:
            if browser:
                await browser.close()


def main() -> None:
    saver = CookieSaver(
        cookie_file=COOKIES_FILE_PATH,
        playwright_context_manager=async_playwright(),
        login_url=LOGIN_URL,
        post_login_indicator=POST_LOGIN_INDICATOR_URL,
        headless_mode=BROWSER_HEADLESS_MODE,
        timeout_ms=DEFAULT_LOGIN_NAVIGATION_TIMEOUT_MS,
    )
    
    success: bool = asyncio.run(saver.save())
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()