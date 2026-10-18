import pytest
from playwright.sync_api import expect
from unittest.mock import Mock
from config import BASE_URL, SAUCE_USERNAME, SAUCE_PASSWORD
from healing.locatorHealer import LocatorHealer
from pages.loginPage.loginPageLocators import usernameInput, passwordInput
from pages.productsPage.productsPageLocators import productsTitle


def test_login_button_healing(page):

    page.goto(BASE_URL)

    page.fill(usernameInput, SAUCE_USERNAME)
    page.fill(passwordInput, SAUCE_PASSWORD)

    healer = LocatorHealer(page)

    healer.clickWithHealing("#login-btn")
    expect(page.locator(productsTitle)).to_be_visible()

@pytest.mark.live_api
def test_gemini_fallback(page):
    page.goto(BASE_URL)

    page.fill(usernameInput, SAUCE_USERNAME)
    page.fill(passwordInput, SAUCE_PASSWORD)

    healer = LocatorHealer(page)

    # Test Gemini directly, without rule-based healing
    healedLocator = healer.findWithGemini("#login-button-old")

    page.locator(healedLocator).click()

    expect(page.locator(productsTitle)).to_be_visible()


def test_gemini_fallback_mocked(page):
    page.goto(BASE_URL)

    page.fill(usernameInput, SAUCE_USERNAME)
    page.fill(passwordInput, SAUCE_PASSWORD)

    healer = LocatorHealer(page)

    mockGemini = Mock()
    mockGemini.suggestLocator.return_value = "#login-button"
    healer.geminiHealer = mockGemini

    healedLocator = healer.findWithGemini("#login-button-old")

    assert healedLocator == "#login-button"

    page.locator(healedLocator).click()

    page.locator(productsTitle).wait_for(state="visible")
    mockGemini.suggestLocator.assert_called_once()

def test_automatic_gemini_fallback(page):
    page.goto(BASE_URL)

    page.fill(usernameInput, SAUCE_USERNAME)
    page.fill(passwordInput, SAUCE_PASSWORD)

    healer = LocatorHealer(page)

    mockGemini = Mock()
    mockGemini.suggestLocator.return_value = "#login-button"
    healer.geminiHealer = mockGemini

    # Force rule-based healing to fail
    healer.findSimilarElement = Mock(return_value=None)

    # Test complete automatic fallback
    healer.clickWithHealing("#login-button-old")

    page.locator(productsTitle).wait_for(state="visible")

    healer.findSimilarElement.assert_called_once_with("#login-button-old")
    mockGemini.suggestLocator.assert_called_once()

def test_input_field_healing(page):
    from healing.locatorHealer import LocatorHealer
    from config import BASE_URL, SAUCE_USERNAME
    from pages.loginPage.loginPageLocators import usernameInput

    page.goto(BASE_URL)

    healer = LocatorHealer(page)

    brokenLocator = usernameInput + "-old"

    healer.fillWithHealing(brokenLocator, SAUCE_USERNAME)

    assert page.locator(usernameInput).input_value() == SAUCE_USERNAME