import json
import asyncio
from pathlib import Path
from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from py_li_engage.config import logger
from py_li_engage.constants.log_messages import LogMessages
from py_li_engage.constants.app_constants import AppConstants


class BrowserSessionManager:
    def __init__(
        self,
        browser_headless_mode: bool,
        command_line_maximized_arg: str,
        default_navigation_timeout_ms: int,
        protocol_timeout_ms: int,
        cookies_file_path: Path,
        utf8_encoding: str,
    ) -> None:
        self.browser_headless_mode = browser_headless_mode
        self.command_line_maximized_arg = command_line_maximized_arg
        self.default_navigation_timeout_ms = default_navigation_timeout_ms
        self.protocol_timeout_ms = protocol_timeout_ms
        self.cookies_file_path = cookies_file_path
        self.utf8_encoding = utf8_encoding

    async def initialize(self) -> tuple[Browser, BrowserContext, Page]:
        logger.info(LogMessages.BROWSER_INIT_INFO)
        p = await async_playwright().start()
        browser: Browser | None = None
        try:
            browser = await p.chromium.launch(
                headless=self.browser_headless_mode,
                args=[self.command_line_maximized_arg]
            )
            context: BrowserContext = await browser.new_context(no_viewport=True)
            page: Page = await context.new_page()

            page.set_default_navigation_timeout(self.default_navigation_timeout_ms)
            page.set_default_timeout(self.protocol_timeout_ms)

            await context.clear_cookies()

            cookies_path: Path = Path(__file__).parent.parent / self.cookies_file_path
            if cookies_path.exists():
                cookies_string: str = cookies_path.read_text(encoding=self.utf8_encoding)
                if cookies_string.strip():
                    cookies: list[dict] = json.loads(cookies_string)
                    await context.add_cookies(cookies)
                    logger.info(LogMessages.SESSION_MANAGER_LOG_PREFIX + LogMessages.COOKIES_INJECTED_SUCCESS_INFO)

            logger.info(LogMessages.SESSION_MANAGER_LOG_PREFIX + LogMessages.BROWSER_INIT_SUCCESS_INFO)
            return browser, context, page
        except Exception as error:
            logger.error(LogMessages.SESSION_MANAGER_LOG_PREFIX + LogMessages.BROWSER_INIT_FAILED_ERROR.format(error))
            if browser:
                await browser.close()
            await p.stop()
            raise


async def test_browser_session_manager() -> None:
    browser_manager = BrowserSessionManager(
        browser_headless_mode=AppConstants.BROWSER_HEADLESS_MODE,
        command_line_maximized_arg=AppConstants.COMMAND_LINE_MAXIMIZED_ARG,
        default_navigation_timeout_ms=AppConstants.DEFAULT_NAVIGATION_TIMEOUT_MS,
        protocol_timeout_ms=AppConstants.PROTOCOL_TIMEOUT_MS,
        cookies_file_path=AppConstants.COOKIES_FILE_PATH,
        utf8_encoding=AppConstants.UTF8_ENCODING,
    )

    browser, _context, page = await browser_manager.initialize()
    try:
        await page.goto("https://www.linkedin.com/feed/")
    finally:
        await browser.close()
    
    
if __name__ == "__main__":
    asyncio.run(test_browser_session_manager())