from healing.locatorHealer import LocatorHealer
from pages.cartPage.cartPageLocators import (
    cartTitle,
    backpackName,
    backpackRemoveButton,
    continueShoppingButton,
    checkoutButton,
)


class CartPage:

    def __init__(self, page):
        self.page = page
        self.healer = LocatorHealer(page)

    def getCartTitle(self):
        return self.page.inner_text(cartTitle)

    def getBackpackName(self):
        return self.page.inner_text(backpackName)

    def removeBackpackFromCart(self):
        self.healer.clickWithHealing(backpackRemoveButton)

    def clickContinueShopping(self):
        self.healer.clickWithHealing(continueShoppingButton)

    def clickCheckout(self):
        self.healer.clickWithHealing(checkoutButton)

    def verifyBackpackRemoved(self):
        return self.page.locator(backpackName).count() == 0
