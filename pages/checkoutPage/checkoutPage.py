from healing.locatorHealer import LocatorHealer
from config import CHECKOUT_FIRST_NAME, CHECKOUT_LAST_NAME, CHECKOUT_POSTAL_CODE
from pages.checkoutPage.checkoutPageLocators import (
    checkoutInfoTitle,
    firstNameInput,
    lastNameInput,
    postalCodeInput,
    cancelButton,
    continueButton,
    checkoutOverviewTitle,
    finishButton,
    thankYouMessage,
    backHomeButton,
)


class CheckoutPage:

    def __init__(self, page):
        self.page = page
        self.healer = LocatorHealer(page)

    def getCheckoutInfoTitle(self):
        return self.page.inner_text(checkoutInfoTitle)

    def enterFirstName(self, firstName):
        self.healer.fillWithHealing(firstNameInput, firstName)

    def enterLastName(self, lastName):
        self.healer.fillWithHealing(lastNameInput, lastName)

    def enterPostalCode(self, postalCode):
        self.healer.fillWithHealing(postalCodeInput, postalCode)

    def clickCancel(self):
        self.healer.clickWithHealing(cancelButton)

    def clickContinue(self):
        self.healer.clickWithHealing(continueButton)

    def fillCustomerInformation(self, firstName, lastName, postalCode):
        self.enterFirstName(firstName)
        self.enterLastName(lastName)
        self.enterPostalCode(postalCode)

    def getCheckoutOverviewTitle(self):
        return self.page.inner_text(checkoutOverviewTitle)

    def clickFinish(self):
        self.healer.clickWithHealing(finishButton)

    def getThankYouMessage(self):
        return self.page.inner_text(thankYouMessage)

    def clickBackHome(self):
        self.healer.clickWithHealing(backHomeButton)

    def completeCheckout(self):
        self.fillCustomerInformation(
            CHECKOUT_FIRST_NAME,
            CHECKOUT_LAST_NAME,
            CHECKOUT_POSTAL_CODE,
        )
        self.clickContinue()
        self.clickFinish()

    def verifyOrderCompleted(self):
        self.page.locator(thankYouMessage).wait_for(state="visible")
        return True
