"""
Environment for Behave Testing
"""

from os import getenv
from selenium import webdriver
import logging

WAIT_SECONDS = int(getenv("WAIT_SECONDS", "60"))
BASE_URL = getenv("BASE_URL", "http://localhost:8080")
DRIVER = getenv("DRIVER", "firefox").lower()


def before_all(context):
    """Executed once before all tests"""
    context.base_url = BASE_URL
    context.wait_seconds = WAIT_SECONDS

    # Setup logging
    setup_logging(context)

    # Select either Chrome or Firefox
    if "firefox" in DRIVER:
        context.driver = get_firefox()
    else:
        context.driver = get_chrome()
    context.driver.implicitly_wait(context.wait_seconds)
    context.config.setup_logging()


def after_all(context):
    """Executed after all tests"""
    context.driver.quit()


######################################################################
# Utility functions to create web drivers
######################################################################


def get_chrome():
    """Creates a headless Chrome driver"""
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")
    return webdriver.Chrome(options=options)


def get_firefox():
    """Creates a headless Firefox driver"""
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    return webdriver.Firefox(options=options)


def setup_logging(context):
    logging.basicConfig(
        filename="behave.log",
        level=logging.INFO,
        filemode="w",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)

    context.logger = logging.getLogger("behave_logger")
