import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from py_li_engage import cookie_saver


@pytest.fixture
def tests_data_dir() -> Path:
    directory = Path(__file__).parent / "tests_data"
    directory.mkdir(exist_ok=True)
    return directory


@pytest.fixture
def mock_cookie_saver(tests_data_dir: Path) -> cookie_saver.CookieSaver:
    cookie_file = tests_data_dir / "test-linkedin-cookies.json"
    playwright_cm = MagicMock()
    return cookie_saver.CookieSaver(
        cookie_file=cookie_file,
        playwright_context_manager=playwright_cm,
        login_url="https://mock.login",
        post_login_indicator="https://mock.feed",
        headless_mode=False,
        timeout_ms=1000,
    )


@pytest.mark.asyncio
async def test_cookie_saver_success(mock_cookie_saver: cookie_saver.CookieSaver) -> None:
    mock_cookies: list[dict[str, str]] = [{"name": "li_at", "value": "token_abc"}]

    mock_page = AsyncMock()
    mock_context = AsyncMock()
    mock_context.cookies.return_value = mock_cookies
    
    mock_browser = AsyncMock()
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page

    mock_playwright = AsyncMock()
    mock_playwright.chromium.launch.return_value = mock_browser
    mock_cookie_saver._playwright_cm.__aenter__.return_value = mock_playwright

    result: bool = await mock_cookie_saver.save()

    assert result is True
    assert mock_cookie_saver._cookie_file.exists()
    assert json.loads(mock_cookie_saver._cookie_file.read_text(encoding="utf-8")) == mock_cookies

    mock_page.goto.assert_awaited_once_with("https://mock.login", wait_until="domcontentloaded")
    mock_page.wait_for_url.assert_awaited_once()
    mock_browser.close.assert_awaited_once()

    mock_cookie_saver._cookie_file.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_cookie_saver_empty_cookies(mock_cookie_saver: cookie_saver.CookieSaver) -> None:
    mock_page = AsyncMock()
    mock_context = AsyncMock()
    mock_context.cookies.return_value = []
    
    mock_browser = AsyncMock()
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page

    mock_playwright = AsyncMock()
    mock_playwright.chromium.launch.return_value = mock_browser
    mock_cookie_saver._playwright_cm.__aenter__.return_value = mock_playwright

    result: bool = await mock_cookie_saver.save()

    assert result is False
    assert not mock_cookie_saver._cookie_file.exists()
    mock_browser.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_cookie_saver_exception_handling(mock_cookie_saver: cookie_saver.CookieSaver) -> None:
    mock_cookie_saver._playwright_cm.__aenter__.side_effect = RuntimeError("Crash")

    result: bool = await mock_cookie_saver.save()

    assert result is False
    assert not mock_cookie_saver._cookie_file.exists()


def test_main_success() -> None:
    with patch("py_li_engage.cookie_saver.asyncio.run", return_value=True) as mock_run, \
         patch("sys.exit") as mock_exit:
        
        cookie_saver.main()
        mock_run.assert_called_once()
        mock_exit.assert_not_called()


def test_main_failure() -> None:
    with patch("py_li_engage.cookie_saver.asyncio.run", return_value=False) as mock_run, \
         patch("sys.exit") as mock_exit:
        
        cookie_saver.main()
        mock_run.assert_called_once()
        mock_exit.assert_called_once_with(1)