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
    
    browser_initializer = MagicMock()
    authenticator = MagicMock()
    storage = cookie_saver.JsonCookieStorage(
        cookie_file=cookie_file,
        json_indent=2,
        encoding="utf-8"
    )

    return cookie_saver.CookieSaver(
        playwright_context_manager=playwright_cm,
        browser_initializer=browser_initializer,
        authenticator=authenticator,
        storage=storage,
    )


@pytest.mark.asyncio
async def test_cookie_saver_success(tests_data_dir: Path) -> None:
    cookie_file = tests_data_dir / "test-linkedin-cookies.json"
    mock_cookies: list[dict[str, str]] = [{"name": "li_at", "value": "token_abc"}]

    mock_page = AsyncMock()
    mock_context = AsyncMock()
    mock_context.cookies.return_value = mock_cookies
    
    mock_browser = AsyncMock()
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page

    mock_playwright = AsyncMock()
    mock_playwright.chromium.launch.return_value = mock_browser

    playwright_cm = MagicMock()
    async def mock_aenter(*args, **kwargs):
        return mock_playwright
    playwright_cm.__aenter__ = mock_aenter
    playwright_cm.__aexit__ = AsyncMock(return_value=None)

    browser_initializer = MagicMock()
    browser_initializer.initialize = AsyncMock(
        return_value=(mock_browser, mock_context, mock_page)
    )
    
    authenticator = MagicMock()
    authenticator.wait_for_login = AsyncMock(return_value=None)
    
    storage = cookie_saver.JsonCookieStorage(
        cookie_file=cookie_file,
        json_indent=2,
        encoding="utf-8"
    )

    saver = cookie_saver.CookieSaver(
        playwright_context_manager=playwright_cm,
        browser_initializer=browser_initializer,
        authenticator=authenticator,
        storage=storage,
    )

    result: bool = await saver.save()

    assert result is True
    assert cookie_file.exists()
    assert json.loads(cookie_file.read_text(encoding="utf-8")) == mock_cookies

    cookie_file.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_cookie_saver_empty_cookies(tests_data_dir: Path) -> None:
    cookie_file = tests_data_dir / "test-linkedin-cookies.json"

    mock_page = AsyncMock()
    mock_context = AsyncMock()
    mock_context.cookies.return_value = []
    
    mock_browser = AsyncMock()
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page

    mock_playwright = AsyncMock()
    mock_playwright.chromium.launch.return_value = mock_browser

    playwright_cm = MagicMock()
    async def mock_aenter(*args, **kwargs):
        return mock_playwright
    playwright_cm.__aenter__ = mock_aenter
    playwright_cm.__aexit__ = AsyncMock(return_value=None)

    browser_initializer = MagicMock()
    browser_initializer.initialize = AsyncMock(
        return_value=(mock_browser, mock_context, mock_page)
    )
    
    authenticator = MagicMock()
    authenticator.wait_for_login = AsyncMock(return_value=None)
    
    storage = cookie_saver.JsonCookieStorage(
        cookie_file=cookie_file,
        json_indent=2,
        encoding="utf-8"
    )

    saver = cookie_saver.CookieSaver(
        playwright_context_manager=playwright_cm,
        browser_initializer=browser_initializer,
        authenticator=authenticator,
        storage=storage,
    )

    result: bool = await saver.save()

    assert result is False
    cookie_file.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_cookie_saver_exception_handling(tests_data_dir: Path) -> None:
    cookie_file = tests_data_dir / "test-linkedin-cookies.json"

    playwright_cm = MagicMock()
    async def mock_aenter(*args, **kwargs):
        raise RuntimeError("Crash")
    playwright_cm.__aenter__ = mock_aenter
    playwright_cm.__aexit__ = AsyncMock(return_value=None)

    browser_initializer = MagicMock()
    authenticator = MagicMock()
    storage = cookie_saver.JsonCookieStorage(
        cookie_file=cookie_file,
        json_indent=2,
        encoding="utf-8"
    )

    saver = cookie_saver.CookieSaver(
        playwright_context_manager=playwright_cm,
        browser_initializer=browser_initializer,
        authenticator=authenticator,
        storage=storage,
    )

    result: bool = await saver.save()

    assert result is False
    cookie_file.unlink(missing_ok=True)


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