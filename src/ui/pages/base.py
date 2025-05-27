from typing import Self

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from src.ui.elements import Element


class BasePage:
    driver: WebDriver
    accept_all_cookies_btn: Element = Element(By.CLASS_NAME, "fc-cta-consent")

    def __init__(self, driver: WebDriver):
        self.driver = driver

    def accept_all_cookies(self) -> Self:
        self.accept_all_cookies_btn.click()
        return self

    def is_page_opened(self) -> bool:
        pass
