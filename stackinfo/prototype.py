from selenium.webdriver import FirefoxOptions
from selenium.webdriver import FirefoxService
from selenium.webdriver import Firefox
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException

import os

home_directory = os.path.expanduser("~")
tor_directory = os.path.join(home_directory, "src", "stackinfo", "tor-browser")
profile_path = os.path.join(
    tor_directory, "Browser", "TorBrowser", "Data", "Browser", "profile.default")
binary_path = os.path.join(tor_directory, "Browser", "firefox")
gecko_driver_path = os.path.join(tor_directory, "geckodriver")

firefox_driver_service = FirefoxService(gecko_driver_path)
firefox_driver_service.port = 2828

firefox_options = FirefoxOptions()
firefox_options.log.level = "trace"
firefox_options.set_preference("marionette.debugging.clicktostart", False)
firefox_options.set_preference("torbrowser.settings.quickstart.enabled", True)
firefox_options.binary_location = binary_path
firefox_options.profile = profile_path

tor_browser = Firefox(firefox_options, firefox_driver_service)


def wait_for_tor_connection(driver: Firefox):
    wait = WebDriverWait(driver, 180)
    wait.until(lambda _: driver.title == "")


def find_content(driver: Firefox):
    try:
        elements = driver.find_elements(By.CLASS_NAME, "site_content")
        if len(elements) != 0:
            return True
        else:
            return False
    except StaleElementReferenceException:
        return False


def wait_for_site_content(driver: Firefox):
    wait = WebDriverWait(driver, 180)
    wait.until(find_content)


with tor_browser:
    wait_for_tor_connection(tor_browser)
    tor_browser.get(
        "hiring.cafe")
    wait_for_site_content(tor_browser)
