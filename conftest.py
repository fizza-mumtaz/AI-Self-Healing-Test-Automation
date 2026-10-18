import re
import base64
from pathlib import Path

import pytest
import pytest_html
from playwright.sync_api import sync_playwright


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed and "page" in item.funcargs:
        folder = Path("reports/screenshots")
        folder.mkdir(parents=True, exist_ok=True)

        name = re.sub(r"[^\w.-]", "_", item.nodeid)
        screenshotPath = folder / f"{name}.png"

        try:
            image = item.funcargs["page"].screenshot(
                path=str(screenshotPath),
                full_page=True
            )

            print(f"\n[SCREENSHOT SAVED] {screenshotPath}")

            extras = getattr(report, "extras", [])
            extras.append(
                pytest_html.extras.png(
                    base64.b64encode(image).decode("utf-8"),
                    name="Failure Screenshot"
                )
            )
            report.extras = extras

        except Exception as error:
            print(f"\n[SCREENSHOT FAILED] {error}")


@pytest.fixture
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        yield page

        browser.close()