import asyncio

import random
from playwright.async_api import Page

from py_li_engage.constants.app_constants import AppConstants
from py_li_engage.constants.log_messages import LogMessages
from py_li_engage.config import logger
from py_li_engage.services.session_manager import BrowserSessionManager


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
    asyncio.run(test_browser_and_human_behaviors())