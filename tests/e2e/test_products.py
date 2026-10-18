from pages.loginPage.loginPage import LoginPage
from pages.productsPage.productsPage import ProductsPage


def test_add_backpack_to_cart(page):

    loginPage = LoginPage(page)
    loginPage.login()

    productsPage = ProductsPage(page)
    productsPage.addBackpackToCart()

    assert productsPage.verifyBackpackAddedToCart()