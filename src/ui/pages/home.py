from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from src.ui.pages.base import BasePage
from src.ui.elements import Element


class ATEHomePage(BasePage):
    logo: Element = Element(By.CSS_SELECTOR, "img[src='/static/images/home/logo.png']")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def is_page_opened(self) -> bool:
        return self.logo.is_displayed()
