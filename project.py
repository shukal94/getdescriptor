import pathlib
import platform

BASE_URL = "https://automationexercise.com"
BIN_DIR = pathlib.Path(".bin").absolute()
CHROMEDRIVER_SYMLINK = BIN_DIR / ("chromedriver.exe" if platform.system() == "Windows" else "chromedriver")
