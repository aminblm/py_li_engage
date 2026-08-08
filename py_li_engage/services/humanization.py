import asyncio
import random
from typing import Set
from playwright.async_api import Page

from py_li_engage.constants.app_constants import AppConstants
from py_li_engage.constants.log_messages import LogMessages
from py_li_engage.config import logger


class SleepEngine:
    def __init__(self, human_delay_variance: float) -> None:
        self.human_delay_variance = human_delay_variance

    async def stochastic_sleep(self, base_ms: float) -> None:
        min_ms: float = base_ms * (1 - self.human_delay_variance)
        max_ms: float = base_ms * (1 + self.human_delay_variance)
        random_ms: float = random.uniform(min_ms, max_ms)
        await asyncio.sleep(random_ms / 1000.0)

    async def random_macro_break(self, min_ms: int, max_ms: int) -> None:
        break_time: int = random.randint(min_ms, max_ms)
        logger.info(LogMessages.HUMANIZATION_LOG_PREFIX + LogMessages.HUMAN_MICRO_BREAK_INFO.format(break_time / 1000.0))
        await asyncio.sleep(break_time / 1000.0)


class ScrollingEngine:
    def __init__(
        self,
        sleep_engine: SleepEngine,
        scroll_offset_px: int,
        scroll_multiplier_factor: float,
        scroll_duration_min_ms: float,
        scroll_duration_max_ms: float,
        js_ease_out_quad_snippet: str,
        stochastic_sleep_ms: float,
        post_load_sleep_ms: float,
    ) -> None:
        self.sleep_engine = sleep_engine
        self.scroll_offset_px = scroll_offset_px
        self.scroll_multiplier_factor = scroll_multiplier_factor
        self.scroll_duration_min_ms = scroll_duration_min_ms
        self.scroll_duration_max_ms = scroll_duration_max_ms
        self.js_ease_out_quad_snippet = js_ease_out_quad_snippet
        self.stochastic_sleep_ms = stochastic_sleep_ms
        self.post_load_sleep_ms = post_load_sleep_ms

    async def smooth_scroll_to_element(self, page: Page, selector: str) -> None:
        logger.info(LogMessages.HUMANIZATION_LOG_PREFIX + LogMessages.HUMAN_SCROLL_ELEMENT_INFO.format(selector))
        locator = page.locator(selector)
        await locator.wait_for(state="visible")
        
        await page.evaluate(
            f"""async (sel) => {{
                const element = document.querySelector(sel);
                if (!element) return;
                element.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
            }}""",
            selector,
        )
        await asyncio.sleep(0.8)
        await self.sleep_engine.stochastic_sleep(self.stochastic_sleep_ms)

    async def _strategy_container_sweep(self, page: Page, step: int) -> float:
        """Production container sweep strategy for multi-context scrolling."""
        return await page.evaluate(f"""() => {{
            let moved = 0;
            const elements = document.querySelectorAll('div, main, section, article');
            for (const el of elements) {{
                if (el.scrollHeight > el.clientHeight && window.getComputedStyle(el).overflowY !== 'hidden') {{
                    el.scrollBy({{ top: {step}, behavior: 'smooth' }});
                    moved = el.scrollTop;
                }}
            }}
            window.scrollBy({{ top: {step}, behavior: 'smooth' }});
            return window.pageYOffset || moved;
        }}""")

    async def human_scroll_scan(self, page: Page) -> None:
        logger.info(LogMessages.HUMANIZATION_LOG_PREFIX + LogMessages.HUMAN_SCROLL_SCAN_INFO)
        try:
            await page.wait_for_load_state("domcontentloaded")
            await asyncio.sleep(1.5)

            step_size = 400
            total_down_steps = random.randint(5, 8)

            # --- Phase 1: Scroll Down Incrementally ---
            for _ in range(total_down_steps):
                await self._strategy_container_sweep(page, step_size)
                await asyncio.sleep(random.uniform(1.0, 1.4))

            # Bottom dwell pause
            await asyncio.sleep(random.uniform(1.5, 2.5))

            # --- Phase 2: Scroll Back Up Incrementally ---
            for _ in range(total_down_steps):
                await self._strategy_container_sweep(page, -step_size)
                await asyncio.sleep(random.uniform(0.7, 1.1))

            # Final safety reset to exact top
            await page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")

            logger.info(LogMessages.HUMANIZATION_LOG_PREFIX + "Scroll sequence completed. Stabilizing layout before next phase...")
            await asyncio.sleep(2.0)

        except Exception as error:
            logger.warning(LogMessages.HUMANIZATION_LOG_PREFIX + LogMessages.HUMAN_SCROLL_SCAN_WARN.format(error))
        
        await self.sleep_engine.stochastic_sleep(self.post_load_sleep_ms)


class ReadingBehavior:
    def __init__(
        self,
        reading_time_min_sec: float,
        reading_time_divisor: float,
        read_jitter_min_factor: float,
        read_jitter_max_factor: float,
    ) -> None:
        self.reading_time_min_sec = reading_time_min_sec
        self.reading_time_divisor = reading_time_divisor
        self.read_jitter_min_factor = read_jitter_min_factor
        self.read_jitter_max_factor = read_jitter_max_factor

    async def reading_dwell_time(self, content_length: int) -> None:
        base_seconds: float = max(self.reading_time_min_sec, content_length / self.reading_time_divisor)
        jittered_seconds: float = base_seconds * random.uniform(self.read_jitter_min_factor, self.read_jitter_max_factor)
        logger.info(LogMessages.HUMANIZATION_LOG_PREFIX + LogMessages.HUMAN_DWELL_TIME_INFO.format(jittered_seconds))
        await asyncio.sleep(jittered_seconds)


class TypingBehavior:
    def __init__(
        self,
        human_typing_min_ms: int,
        human_typing_max_ms: int,
        punctuation_delay_min_ms: int,
        punctuation_delay_max_ms: int,
        punctuation_chars: Set[str],
    ) -> None:
        self.human_typing_min_ms = human_typing_min_ms
        self.human_typing_max_ms = human_typing_max_ms
        self.punctuation_delay_min_ms = punctuation_delay_min_ms
        self.punctuation_delay_max_ms = punctuation_delay_max_ms
        self.punctuation_chars = punctuation_chars

    async def human_type(self, page: Page, selector: str, text: str) -> None:
        logger.info(LogMessages.HUMANIZATION_LOG_PREFIX + LogMessages.HUMAN_TYPE_INFO.format(selector))
        locator = page.locator(selector)
        await locator.wait_for(state="visible")
        await locator.focus()

        for char in text:
            await page.keyboard.type(char)
            delay: int = random.randint(self.human_typing_min_ms, self.human_typing_max_ms)
            if char in self.punctuation_chars:
                delay += random.randint(self.punctuation_delay_min_ms, self.punctuation_delay_max_ms)
            await asyncio.sleep(delay / 1000.0)

        await locator.dispatch_event("input")
        await locator.dispatch_event("change")


# --- Production Entrypoint / Testing Harness ---

async def test_humanization_modules() -> None:
    from py_li_engage.services.browser import BrowserSessionManager

    browser_manager = BrowserSessionManager(
        browser_headless_mode=AppConstants.BROWSER_HEADLESS_MODE,
        command_line_maximized_arg=AppConstants.COMMAND_LINE_MAXIMIZED_ARG,
        default_navigation_timeout_ms=AppConstants.DEFAULT_NAVIGATION_TIMEOUT_MS,
        protocol_timeout_ms=AppConstants.PROTOCOL_TIMEOUT_MS,
        cookies_file_path=AppConstants.COOKIES_FILE_PATH,
        utf8_encoding=AppConstants.UTF8_ENCODING,
    )

    sleep_engine = SleepEngine(human_delay_variance=AppConstants.HUMAN_DELAY_VARIANCE)
    scrolling_engine = ScrollingEngine(
        sleep_engine=sleep_engine,
        scroll_offset_px=AppConstants.SCROLL_OFFSET_PX,
        scroll_multiplier_factor=AppConstants.SCROLL_MULTIPLIER_FACTOR,
        scroll_duration_min_ms=AppConstants.SCROLL_DURATION_MIN_MS,
        scroll_duration_max_ms=AppConstants.SCROLL_DURATION_MAX_MS,
        js_ease_out_quad_snippet=AppConstants.JS_EASE_OUT_QUAD_SNIPPET,
        stochastic_sleep_ms=AppConstants.STOCHASTIC_SLEEP_MS,
        post_load_sleep_ms=AppConstants.POST_LOAD_SLEEP_MS,
    )
    reading_behavior = ReadingBehavior(
        reading_time_min_sec=AppConstants.READING_TIME_MIN_SEC,
        reading_time_divisor=AppConstants.READING_TIME_DIVISOR,
        read_jitter_min_factor=AppConstants.READ_JITTER_MIN_FACTOR,
        read_jitter_max_factor=AppConstants.READ_JITTER_MAX_FACTOR,
    )
    typing_behavior = TypingBehavior(
        human_typing_min_ms=AppConstants.HUMAN_TYPING_MIN_MS,
        human_typing_max_ms=AppConstants.HUMAN_TYPING_MAX_MS,
        punctuation_delay_min_ms=AppConstants.PUNCTUATION_DELAY_MIN_MS,
        punctuation_delay_max_ms=AppConstants.PUNCTUATION_DELAY_MAX_MS,
        punctuation_chars={".", ",", "!", "?", " "},
    )

    browser, _context, page = await browser_manager.initialize()
    try:
        await page.goto(AppConstants.POST_LOGIN_INDICATOR_URL)
        
        # Execute vertical scan behavior with production container sweep
        await scrolling_engine.human_scroll_scan(page)
        
        # Execute content reading dwell time simulation
        await reading_behavior.reading_dwell_time(content_length=250)
        
        # Execute stochastic delay and macro pause breaks
        await sleep_engine.stochastic_sleep(base_ms=AppConstants.SLEEP_SHORT_MS)
        await sleep_engine.random_macro_break(
            min_ms=AppConstants.MACRO_BREAK_MIN_MS,
            max_ms=AppConstants.MACRO_BREAK_MAX_MS,
        )
    finally:
        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_humanization_modules())