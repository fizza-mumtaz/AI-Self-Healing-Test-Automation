import pytest
from healing.geminiHealer import GeminiHealer
from unittest.mock import patch
from config import SECOND_SITE_URL, SECOND_SITE_USERNAME
from healing.locatorHealer import LocatorHealer
from pages.secondSite.secondSiteLocators import (
    usernameInput,
    passwordInput,
)


def test_cross_website_input_healing(page):

    page.goto(SECOND_SITE_URL)

    healer = LocatorHealer(page)

    brokenLocator = usernameInput + "-old"

    healer.fillWithHealing(brokenLocator, SECOND_SITE_USERNAME)

    assert page.locator(usernameInput).input_value() == SECOND_SITE_USERNAME

def test_cross_website_gemini_healing(page):

    page.goto(SECOND_SITE_URL)

    healer = LocatorHealer(page)

    brokenLocator = "#completely-different-locator"

    with patch.object(healer, "findSimilarElement", return_value=None):
        with patch.object(
            healer,
            "findWithGemini",
            return_value=usernameInput
        ) as mockGemini:

            healer.fillWithHealing(brokenLocator, SECOND_SITE_USERNAME)

            mockGemini.assert_called_once_with(
                brokenLocator,
                action="fill"
            )

    assert page.locator(usernameInput).input_value() == SECOND_SITE_USERNAME

def test_cross_website_gemini_validation(page):

    page.goto(SECOND_SITE_URL)

    healer = LocatorHealer(page)

    brokenLocator = usernameInput + "-old"

    with patch.object(healer, "findSimilarElement", return_value=None):

        with patch.object(
            GeminiHealer,
            "suggestLocator",
            return_value=usernameInput
        ) as mockSuggestion:

            healer.fillWithHealing(brokenLocator, SECOND_SITE_USERNAME)

            mockSuggestion.assert_called_once()

    assert page.locator(usernameInput).input_value() == SECOND_SITE_USERNAME

def test_gemini_rejects_wrong_locator(page):

    page.goto(SECOND_SITE_URL)

    healer = LocatorHealer(page)

    brokenLocator = usernameInput + "-old"

    with patch.object(healer, "findSimilarElement", return_value=None):

        with patch.object(
            GeminiHealer,
            "suggestLocator",
            return_value=passwordInput
        ) as mockSuggestion:

            with pytest.raises(Exception, match="Unsafe Gemini replacement"):
                healer.fillWithHealing(brokenLocator, SECOND_SITE_USERNAME)

            mockSuggestion.assert_called_once()

    assert page.locator(usernameInput).input_value() == ""
    assert page.locator(passwordInput).input_value() == ""