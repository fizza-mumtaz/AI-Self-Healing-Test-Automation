from pages.loginPage.loginPage import LoginPage


def test_valid_login(page):

    loginPage = LoginPage(page)

    loginPage.login()

    assert loginPage.isLoginSuccessful()