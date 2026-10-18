from healing.locatorHealer import LocatorHealer
from config import BASE_URL, SAUCE_USERNAME, SAUCE_PASSWORD
from pages.loginPage.loginPageLocators import (
    usernameInput,
    passwordInput,
    loginButton
)
from pages.productsPage.productsPageLocators import productsTitle


class LoginPage:

    def __init__(self, page):
        self.page = page
        self.healer = LocatorHealer(page)

    def openLoginPage(self):
        self.page.goto(BASE_URL)

    def enterUsername(self, username):
        self.healer.fillWithHealing(usernameInput, username)

    def enterPassword(self, password):
        self.healer.fillWithHealing(passwordInput, password)

    def clickLogin(self):
        self.healer.clickWithHealing(loginButton)

    def login(self):
        self.openLoginPage()
        self.enterUsername(SAUCE_USERNAME)
        self.enterPassword(SAUCE_PASSWORD)
        self.clickLogin()

    def isLoginSuccessful(self):
        self.page.locator(productsTitle).wait_for(state="visible")
        return True