from typing import Self

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Element:
    def __init__(self, by: By, value: str, wait: bool=False, timeout: int=10):
        self.by = by
        self.value = value
        self.wait = wait
        self.timeout = timeout

    def __get__(self, instance, owner) -> Self | WebElement:
        if instance is None:
            return self
        return self._find(instance)

    def _find(self, instance) -> WebElement:
        driver: WebDriver = instance.driver
        if self.wait:
            wait = WebDriverWait(driver, self.timeout)
            return wait.until(EC.presence_of_element_located((str(self.by), self.value)))
        return driver.find_element(self.by, self.value)

    def exists(self, instance) -> bool:
        try:
            instance.driver.find_element(self.by, self.value)
            return True
        except NoSuchElementException:
            return False

    def is_displayed(self, instance) -> bool:
        try:
            return self._find(instance).is_displayed()
        except (NoSuchElementException, StaleElementReferenceException):
            return False

    def text(self, instance) -> str | None:
        try:
            return self._find(instance).text
        except (NoSuchElementException, StaleElementReferenceException):
            return None
