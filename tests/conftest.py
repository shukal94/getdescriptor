import pytest
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver

import project
import src.utils as utils
from selenium import webdriver


@pytest.fixture(scope="session", autouse=True)
def before_all():
    utils.install_or_update_chromedriver_and_cft()


@pytest.fixture()
def driver() -> WebDriver:
    return webdriver.Chrome(
        service=Service(
            executable_path=f"{project.BIN_DIR}/chromedriver"
        )
    )


@pytest.fixture(autouse=True)
def before_test(driver: WebDriver):
    driver.get(project.BASE_URL)

    yield

    driver.quit()
