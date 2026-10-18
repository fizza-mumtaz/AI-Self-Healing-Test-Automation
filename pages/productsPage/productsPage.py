from healing.locatorHealer import LocatorHealer
from pages.productsPage.productsPageLocators import (
    productsTitle,
    backpackName,
    backpackAddToCartButton,
    backpackRemoveButton,
    shoppingCartIcon,
    cartBadge,
)


class ProductsPage:

    def __init__(self, page):
        self.page = page
        self.healer = LocatorHealer(page)

    def getProductsTitle(self):
        return self.page.inner_text(productsTitle)

    def getBackpackName(self):
        return self.page.inner_text(backpackName)

    def addBackpackToCart(self):
        self.healer.clickWithHealing(backpackAddToCartButton)

    def removeBackpackFromProducts(self):
        self.healer.clickWithHealing(backpackRemoveButton)

    def openShoppingCart(self):
        self.healer.clickWithHealing(shoppingCartIcon)

    def getCartBadgeCount(self):
        return self.page.inner_text(cartBadge)

    def verifyBackpackAddedToCart(self):
        return self.getCartBadgeCount() == "1"
