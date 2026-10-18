from pages.loginPage.loginPage import LoginPage
from pages.productsPage.productsPage import ProductsPage
from pages.cartPage.cartPage import CartPage
from pages.checkoutPage.checkoutPage import CheckoutPage


def test_complete_checkout(page):

    loginPage = LoginPage(page)
    loginPage.login()

    productsPage = ProductsPage(page)
    productsPage.addBackpackToCart()
    productsPage.openShoppingCart()

    cartPage = CartPage(page)
    cartPage.clickCheckout()

    checkoutPage = CheckoutPage(page)
    checkoutPage.completeCheckout()

    assert checkoutPage.verifyOrderCompleted()