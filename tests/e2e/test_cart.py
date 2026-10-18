from pages.loginPage.loginPage import LoginPage
from pages.productsPage.productsPage import ProductsPage
from pages.cartPage.cartPage import CartPage


def test_remove_backpack_from_cart(page):

    loginPage = LoginPage(page)
    loginPage.login()

    productsPage = ProductsPage(page)
    productsPage.addBackpackToCart()
    productsPage.openShoppingCart()

    cartPage = CartPage(page)
    cartPage.removeBackpackFromCart()

    assert cartPage.verifyBackpackRemoved()