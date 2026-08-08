import asyncio
import json
import random
import re
from pathlib import Path
import httpx
from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from py_li_engage.constants.app_constants import AppConstants
from py_li_engage.constants.app_secrets import AppSecrets
from py_li_engage.constants.log_messages import LogMessages
from py_li_engage.config import logger


class CommentCleaner:
    def __init__(
        self,
        comment_clean_regex_unicode: str,
        quote_strip_pattern: str,
        dash_spacing_pattern: str,
    ) -> None:
        self.comment_clean_regex_unicode = comment_clean_regex_unicode
        self.quote_strip_pattern = quote_strip_pattern
        self.dash_spacing_pattern = dash_spacing_pattern

    def clean(self, raw_comment: str) -> str:
        logger.info(LogMessages.COMMENT_SERVICE_LOG_PREFIX + LogMessages.CLEANING_COMMENT_INFO)
        if not raw_comment:
            return ""
            
        emoji_regex: re.Pattern = re.compile(self.comment_clean_regex_unicode, re.UNICODE)
        cleaned: str = re.sub(self.quote_strip_pattern, "", raw_comment)
        cleaned = re.sub(self.dash_spacing_pattern, ", ", cleaned)
        cleaned = emoji_regex.sub("", cleaned)
        return cleaned.strip()


class GroqService:
    def __init__(
        self,
        api_key: str,
        comment_cleaner: CommentCleaner,
        groq_comment_prompt_template: str,
        groq_model_name: str,
        groq_role_user: str,
        groq_request_timeout_sec: float,
        groq_api_url: str,
    ) -> None:
        self.api_key = api_key
        self.comment_cleaner = comment_cleaner
        self.groq_comment_prompt_template = groq_comment_prompt_template
        self.groq_model_name = groq_model_name
        self.groq_role_user = groq_role_user
        self.groq_request_timeout_sec = groq_request_timeout_sec
        self.groq_api_url = groq_api_url

    async def generate_comment(self, post_content: str) -> str:
        logger.info(LogMessages.GROQ_SERVICE_LOG_PREFIX + LogMessages.GROQ_API_REQUEST_INFO)
        prompt: str = self.groq_comment_prompt_template.format(post_content=post_content)
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload: dict[str, str | list[dict[str, str]]] = {
            "model": self.groq_model_name,
            "messages": [{"role": self.groq_role_user, "content": prompt}],
        }

        try:
            async with httpx.AsyncClient(timeout=self.groq_request_timeout_sec) as client:
                response = await client.post(self.groq_api_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                raw_comment: str = (
                    data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                    .strip()
                )
                logger.info(LogMessages.GROQ_SERVICE_LOG_PREFIX + LogMessages.GROQ_API_SUCCESS_INFO)
                return self.comment_cleaner.clean(raw_comment)
        except Exception as error:
            logger.error(LogMessages.GROQ_SERVICE_LOG_PREFIX + LogMessages.GROQ_API_ERROR_ERROR.format(error))
            raise


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


class HumanBehaviorUtility:
    def __init__(
        self,
        human_delay_variance: float,
        reading_time_min_sec: float,
        reading_time_divisor: float,
        read_jitter_min_factor: float,
        read_jitter_max_factor: float,
        scroll_offset_px: int,
        scroll_multiplier_factor: float,
        scroll_duration_min_ms: float,
        scroll_duration_max_ms: float,
        js_ease_out_quad_snippet: str,
        stochastic_sleep_ms: float,
        post_load_sleep_ms: float,
        human_typing_min_ms: int,
        human_typing_max_ms: int,
        punctuation_delay_min_ms: int,
        punctuation_delay_max_ms: int,
        punctuation_chars: set[str],
    ) -> None:
        self.human_delay_variance = human_delay_variance
        self.reading_time_min_sec = reading_time_min_sec
        self.reading_time_divisor = reading_time_divisor
        self.read_jitter_min_factor = read_jitter_min_factor
        self.read_jitter_max_factor = read_jitter_max_factor
        self.scroll_offset_px = scroll_offset_px
        self.scroll_multiplier_factor = scroll_multiplier_factor
        self.scroll_duration_min_ms = scroll_duration_min_ms
        self.scroll_duration_max_ms = scroll_duration_max_ms
        self.js_ease_out_quad_snippet = js_ease_out_quad_snippet
        self.stochastic_sleep_ms = stochastic_sleep_ms
        self.post_load_sleep_ms = post_load_sleep_ms
        self.human_typing_min_ms = human_typing_min_ms
        self.human_typing_max_ms = human_typing_max_ms
        self.punctuation_delay_min_ms = punctuation_delay_min_ms
        self.punctuation_delay_max_ms = punctuation_delay_max_ms
        self.punctuation_chars = punctuation_chars

    async def stochastic_sleep(self, base_ms: float) -> None:
        min_ms: float = base_ms * (1 - self.human_delay_variance)
        max_ms: float = base_ms * (1 + self.human_delay_variance)
        random_ms: float = random.uniform(min_ms, max_ms)
        await asyncio.sleep(random_ms / 1000.0)

    async def random_macro_break(self, min_ms: int, max_ms: int) -> None:
        break_time: int = random.randint(min_ms, max_ms)
        logger.info(LogMessages.HUMANIZATION_LOG_PREFIX + LogMessages.HUMAN_MICRO_BREAK_INFO.format(break_time / 1000.0))
        await asyncio.sleep(break_time / 1000.0)

    async def reading_dwell_time(self, content_length: int) -> None:
        base_seconds: float = max(self.reading_time_min_sec, content_length / self.reading_time_divisor)
        jittered_seconds: float = base_seconds * random.uniform(self.read_jitter_min_factor, self.read_jitter_max_factor)
        logger.info(LogMessages.HUMANIZATION_LOG_PREFIX + LogMessages.HUMAN_DWELL_TIME_INFO.format(jittered_seconds))
        await asyncio.sleep(jittered_seconds)

    async def smooth_scroll_to_element(self, page: Page, selector: str) -> None:
        logger.info(LogMessages.HUMANIZATION_LOG_PREFIX + LogMessages.HUMAN_SCROLL_ELEMENT_INFO.format(selector))
        await page.wait_for_selector(selector)
        
        await page.evaluate(
            f"""async (sel) => {{
                const element = document.querySelector(sel);
                if (!element) return;

                const targetPosition = element.getBoundingClientRect().top + window.pageYOffset - {self.scroll_offset_px};
                const startPosition = window.pageYOffset;
                const distance = targetPosition - startPosition;
                const duration = Math.min(Math.max(Math.abs(distance) * {self.scroll_multiplier_factor}, {self.scroll_duration_min_ms}), {self.scroll_duration_max_ms});
                let startTime = null;

                {self.js_ease_out_quad_snippet}

                await new Promise((resolve) => {{
                    function step(currentTime) {{
                        if (!startTime) startTime = currentTime;
                        const timeElapsed = currentTime - startTime;
                        const progress = Math.min(timeElapsed / duration, 1);
                        const ease = easeOutQuad(progress);
                        
                        window.scrollTo(0, startPosition + distance * ease);
                        
                        if (progress < 1) {{
                            requestAnimationFrame(step);
                        }} else {{
                            resolve();
                        }}
                    }}
                    requestAnimationFrame(step);
                }});
            }}""",
            selector,
        )
        await self.stochastic_sleep(self.stochastic_sleep_ms)

    async def human_scroll_scan(self, page: Page) -> None:
        logger.info(LogMessages.HUMANIZATION_LOG_PREFIX + LogMessages.HUMAN_SCROLL_SCAN_INFO)
        try:
            await page.evaluate(
                """async () => {
                    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
                    const scrollCount = Math.floor(Math.random() * 3) + 2;
                    
                    for (let i = 0; i < scrollCount; i++) {
                        const scrollAmount = Math.floor(Math.random() * 300) + 200;
                        window.scrollBy({ top: scrollAmount, behavior: 'smooth' });
                        await sleep(Math.floor(Math.random() * 800) + 600);
                    }
                    
                    if (Math.random() > 0.5) {
                        window.scrollBy({ top: -150, behavior: 'smooth' });
                        await sleep(600);
                    }
                }"""
            )
        except Exception as error:
            logger.warning(LogMessages.HUMANIZATION_LOG_PREFIX + LogMessages.HUMAN_SCROLL_SCAN_WARN.format(error))
        
        await self.stochastic_sleep(self.post_load_sleep_ms)

    async def human_type(self, page: Page, selector: str, text: str) -> None:
        logger.info(LogMessages.HUMANIZATION_LOG_PREFIX + LogMessages.HUMAN_TYPE_INFO.format(selector))
        await page.wait_for_selector(selector)
        await page.click(selector)

        for char in text:
            await page.keyboard.type(char)
            delay: int = random.randint(self.human_typing_min_ms, self.human_typing_max_ms)
            if char in self.punctuation_chars:
                delay += random.randint(self.punctuation_delay_min_ms, self.punctuation_delay_max_ms)
            await asyncio.sleep(delay / 1000.0)

        await page.evaluate(
            """(sel) => {
                const box = document.querySelector(sel);
                if (box) {
                    box.dispatchEvent(new Event('input', { bubbles: true }));
                    box.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }""",
            selector,
        )


# --- Live Testing Main Entrypoints ---

async def test_comment_cleaner() -> None:
    cleaner = CommentCleaner(
        comment_clean_regex_unicode=AppConstants.COMMENT_CLEAN_REGEX_UNICODE,
        quote_strip_pattern=AppConstants.QUOTE_STRIP_PATTERN,
        dash_spacing_pattern=AppConstants.DASH_SPACING_PATTERN
    )
    raw = '\"Great insights🔥 - loved it!\"'
    cleaned = cleaner.clean(raw_comment=raw)
    print(f"Cleaned Comment: {cleaned}")


async def test_groq_service() -> None:
    cleaner = CommentCleaner(
        comment_clean_regex_unicode=AppConstants.COMMENT_CLEAN_REGEX_UNICODE,
        quote_strip_pattern=AppConstants.QUOTE_STRIP_PATTERN,
        dash_spacing_pattern=AppConstants.DASH_SPACING_PATTERN,
    )
    groq_service = GroqService(
        api_key=AppSecrets.GROQ_API_KEY,
        comment_cleaner=cleaner,
        groq_comment_prompt_template=AppConstants.GROQ_COMMENT_PROMPT_TEMPLATE,
        groq_model_name=AppConstants.GROQ_MODEL_NAME,
        groq_role_user=AppConstants.GROQ_ROLE_USER,
        groq_request_timeout_sec=AppConstants.GROQ_REQUEST_TIMEOUT_SEC,
        groq_api_url=AppConstants.GROQ_API_URL,
    )
    post_text = "AI agents are transforming how we build backend software architectures."
    try:
        comment = await groq_service.generate_comment(post_content=post_text)
        print(f"Cleaned generated Groq Comment: {comment}")
    except Exception as e:
        print(f"Groq Test Failed: {e}")


async def test_browser_and_human_behaviors() -> None:
    browser_manager = BrowserSessionManager(
        browser_headless_mode=AppConstants.BROWSER_HEADLESS_MODE,
        command_line_maximized_arg=AppConstants.COMMAND_LINE_MAXIMIZED_ARG,
        default_navigation_timeout_ms=AppConstants.DEFAULT_NAVIGATION_TIMEOUT_MS,
        protocol_timeout_ms=AppConstants.PROTOCOL_TIMEOUT_MS,
        cookies_file_path=AppConstants.COOKIES_FILE_PATH,
        utf8_encoding=AppConstants.UTF8_ENCODING,
    )
    human_utility = HumanBehaviorUtility(
        human_delay_variance=AppConstants.HUMAN_DELAY_VARIANCE,
        reading_time_min_sec=AppConstants.READING_TIME_MIN_SEC,
        reading_time_divisor=AppConstants.READING_TIME_DIVISOR,
        read_jitter_min_factor=AppConstants.READ_JITTER_MIN_FACTOR,
        read_jitter_max_factor=AppConstants.READ_JITTER_MAX_FACTOR,
        scroll_offset_px=AppConstants.SCROLL_OFFSET_PX,
        scroll_multiplier_factor=AppConstants.SCROLL_MULTIPLIER_FACTOR,
        scroll_duration_min_ms=AppConstants.SCROLL_DURATION_MIN_MS,
        scroll_duration_max_ms=AppConstants.SCROLL_DURATION_MAX_MS,
        js_ease_out_quad_snippet=AppConstants.JS_EASE_OUT_QUAD_SNIPPET,
        stochastic_sleep_ms=AppConstants.STOCHASTIC_SLEEP_MS,
        post_load_sleep_ms=AppConstants.POST_LOAD_SLEEP_MS,
        human_typing_min_ms=AppConstants.HUMAN_TYPING_MIN_MS,
        human_typing_max_ms=AppConstants.HUMAN_TYPING_MAX_MS,
        punctuation_delay_min_ms=AppConstants.PUNCTUATION_DELAY_MIN_MS,
        punctuation_delay_max_ms=AppConstants.PUNCTUATION_DELAY_MAX_MS,
        punctuation_chars={".", ",", "!", "?", " "},
    )

    browser, _context, page = await browser_manager.initialize()
    try:
        await page.goto("https://www.linkedin.com/feed/")
        await human_utility.human_scroll_scan(page)
        await human_utility.reading_dwell_time(content_length=150)
        await human_utility.stochastic_sleep(base_ms=AppConstants.SLEEP_SHORT_MS)
        await human_utility.random_macro_break(
            min_ms=AppConstants.MACRO_BREAK_MIN_MS,
            max_ms=AppConstants.MACRO_BREAK_MAX_MS,
        )
    finally:
        await browser.close()


if __name__ == "__main__":
    # asyncio.run(test_comment_cleaner())
    # asyncio.run(test_groq_service())
    asyncio.run(test_browser_and_human_behaviors())