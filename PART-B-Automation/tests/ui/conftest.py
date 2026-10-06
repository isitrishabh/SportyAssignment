"""UI fixtures: Chrome driver lifecycle, page objects and failure screenshots."""
import re

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config.settings import settings
from pages.betting_page import BettingPage


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Expose each phase's report on the test item so fixtures can react to failures."""
    outcome = yield
    setattr(item, f"report_{call.when}", outcome.get_result())


@pytest.fixture
def driver(request):
    options = Options()
    options.add_argument("--window-size=1440,900")  # the app targets desktop layouts
    if settings.headless:
        options.add_argument("--headless=new")
    chrome = webdriver.Chrome(options=options)  # Selenium Manager resolves the driver

    yield chrome

    report = getattr(request.node, "report_call", None)
    if report is not None and report.failed:
        settings.screenshot_dir.mkdir(parents=True, exist_ok=True)
        name = re.sub(r"[^\w.-]", "_", request.node.name)
        chrome.save_screenshot(str(settings.screenshot_dir / f"{name}.png"))
        allure.attach(chrome.get_screenshot_as_png(), "failure screenshot", allure.attachment_type.PNG)
        allure.attach(chrome.page_source, "page source", allure.attachment_type.HTML)
    chrome.quit()


@pytest.fixture
def betting_page(driver) -> BettingPage:
    return BettingPage(driver, settings.app_url, settings.ui_timeout)
