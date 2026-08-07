import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

COOKIE_FILE = Path("data/linkedin-cookies.json")
LOGIN_URL = "https://www.linkedin.com/login"
LOGIN_WAIT_TIMEOUT = 60000  # 60 seconds


async def save_linkedin_cookies() -> None:
    """Launches a browser for manual LinkedIn login and saves session cookies."""
    async with async_playwright() as p:
        # Launch browser in headed mode maximized
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            no_viewport=True  # Respects maximized/custom window bounds
        )
        page = await context.new_page()

        print(f"Navigating to {LOGIN_URL}...")
        await page.goto(LOGIN_URL, wait_until="domcontentloaded")

        print(
            f"Please log in manually. Waiting {LOGIN_WAIT_TIMEOUT // 1000} seconds..."
        )
        await asyncio.sleep(LOGIN_WAIT_TIMEOUT / 1000)

        # Extract and save cookies securely
        cookies = await context.cookies()
        COOKIE_FILE.write_text(json.dumps(cookies, indent=2), encoding="utf-8")

        print(f"Success! Cookies saved to {COOKIE_FILE.resolve()}")
        await browser.close()


def main() -> None:
    asyncio.run(save_linkedin_cookies())


if __name__ == "__main__":
    main()