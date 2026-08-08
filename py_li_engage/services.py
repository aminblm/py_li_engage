import asyncio
import json
import random
import re
from pathlib import Path
import httpx
from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from py_li_engage.config import (
    COOKIES_FILE_NAME,
    GROQ_API_URL,
    GROQ_MODEL_NAME,
    BROWSER_HEADLESS_MODE,
    NAVIGATION_TIMEOUT_MS,
    PROTOCOL_TIMEOUT_MS,
    HUMAN_DELAY_VARIANCE,
    HUMAN_TYPING_MAX_MS,
    HUMAN_TYPING_MIN_MS,
    logger,
)


class CommentCleaner:

    @staticmethod
    def clean(raw_comment: str) -> str:
        logger.info("Cleaning generated comment text.")
        if not raw_comment:
            return ""
        # Emoji regex unicode range block
        emoji_regex = re.compile(
            r"[\U0001f000-\U0001f6ff\U0001f900-\U0001f9ff\U0001fa00-\U0001fa6f\U0001fa70-\U0001faff\u2600-\u27bf]",
            re.UNICODE,
        )
        cleaned = re.sub(r"^[\"\']+|[\"\']+$", "", raw_comment)
        cleaned = re.sub(r"^(?:\[Workflow\]\s*)?Generated Short Comment:\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*-\s*", ", ", cleaned)
        cleaned = emoji_regex.sub("", cleaned)
        return cleaned.strip()


class GroqService:

    @staticmethod
    async def generate_comment(api_key: str, post_content: str) -> str:
        logger.info("Initiating request to Groq API for comment generation.")
        prompt = (
            f'Write the shortest and most engaging professional comment for this LinkedIn post content: "{post_content}". '
            "Do NOT include any emojis whatsoever."
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        payload = {
            "model": GROQ_MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}],
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(GROQ_API_URL, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                raw_comment = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                logger.info("Groq comment generation successful.")
                return CommentCleaner.clean(raw_comment)
        except Exception as error:
            logger.error(f"Error communicating with Groq API: {error}")
            raise


class BrowserSessionManager:

    @staticmethod
    async def initialize() -> tuple[Browser, BrowserContext, Page]:
        logger.info("Initializing Playwright browser session.")
        p = await async_playwright().start()
        browser = None
        try:
            browser = await p.chromium.launch(
                headless=BROWSER_HEADLESS_MODE,
                args=["--start-maximized"]
            )
            # Create persistent non-fixed context for maximized resolution handling
            context = await browser.new_context(no_viewport=True)
            page = await context.new_page()

            page.set_default_navigation_timeout(NAVIGATION_TIMEOUT_MS)
            page.set_default_timeout(PROTOCOL_TIMEOUT_MS)

            # Clear cache and local cookies before injection
            await context.clear_cookies()

            cookies_path = Path(__file__).parent.parent / COOKIES_FILE_NAME
            if cookies_path.exists():
                cookies_string = cookies_path.read_text(encoding="utf-8")
                if cookies_string.strip():
                    cookies = json.loads(cookies_string)
                    await context.add_cookies(cookies)
                    logger.info("Cookies injected successfully.")

            logger.info("Browser session initialized successfully.")
            return browser, context, page
        except Exception as error:
            logger.error(f"Failed to initialize browser session: {error}")
            if browser:
                await browser.close()
            await p.stop()
            raise


class HumanBehaviorUtility:

    @staticmethod
    async def stochastic_sleep(base_ms: float) -> None:
        variance = HUMAN_DELAY_VARIANCE
        min_ms = base_ms * (1 - variance)
        max_ms = base_ms * (1 + variance)
        random_ms = random.uniform(min_ms, max_ms)
        await asyncio.sleep(random_ms / 1000.0)

    @staticmethod
    async def random_macro_break(min_ms: int, max_ms: int) -> None:
        break_time = random.randint(min_ms, max_ms)
        logger.info(f"[Humanization] Taking a natural human micro-break for {(break_time / 1000.0):.1f} seconds...")
        await asyncio.sleep(break_time / 1000.0)

    @staticmethod
    async def reading_dwell_time(content_length: int) -> None:
        base_seconds = max(3.0, content_length / 18.0)
        jittered_seconds = base_seconds * random.uniform(0.8, 1.2)
        logger.info(f"[Humanization] Simulating reading dwell time for {jittered_seconds:.1f} seconds based on post length.")
        await asyncio.sleep(jittered_seconds)

    @staticmethod
    async def smooth_scroll_to_element(page: Page, selector: str) -> None:
        logger.info(f"[Humanization] Scrolling organically to element: {selector}")
        await page.wait_for_selector(selector)
        
        await page.evaluate(
            """async (sel) => {
                const element = document.querySelector(sel);
                if (!element) return;

                const targetPosition = element.getBoundingClientRect().top + window.pageYOffset - 200;
                const startPosition = window.pageYOffset;
                const distance = targetPosition - startPosition;
                const duration = Math.min(Math.max(Math.abs(distance) * 0.5, 400), 1500);
                let startTime = null;

                function easeOutQuad(t) { return t * (2 - t); }

                await new Promise((resolve) => {
                    function step(currentTime) {
                        if (!startTime) startTime = currentTime;
                        const timeElapsed = currentTime - startTime;
                        const progress = Math.min(timeElapsed / duration, 1);
                        const ease = easeOutQuad(progress);
                        
                        window.scrollTo(0, startPosition + distance * ease);
                        
                        if (progress < 1) {
                            requestAnimationFrame(step);
                        } else {
                            resolve();
                        }
                    }
                    requestAnimationFrame(step);
                });
            }""",
            selector,
        )
        await HumanBehaviorUtility.stochastic_sleep(800)

    @staticmethod
    async def human_scroll_scan(page: Page) -> None:
        logger.info("[Humanization] Performing organic scroll-and-scan behavior on page load...")
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
            logger.warning(f"[Humanization] Non-critical error during page scroll scan: {error}")
        
        await HumanBehaviorUtility.stochastic_sleep(1000)

    @staticmethod
    async def human_type(page: Page, selector: str, text: str) -> None:
        logger.info(f"[Humanization] Typing text organically into selector: {selector}")
        await page.wait_for_selector(selector)
        await page.click(selector)

        for char in text:
            await page.keyboard.type(char)
            delay = random.randint(HUMAN_TYPING_MIN_MS, HUMAN_TYPING_MAX_MS)
            if char in {".", ",", "!", "?", " "}:
                delay += random.randint(150, 450)
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