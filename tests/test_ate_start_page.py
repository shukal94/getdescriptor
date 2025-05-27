import pytest

from src.ui.pages.home import ATEHomePage


@pytest.mark.smoke
def test_start_page_opens(driver):
    start_page: ATEHomePage = ATEHomePage(driver)
    start_page.accept_all_cookies()
    assert start_page.is_page_opened(), "Start page is not opened."
