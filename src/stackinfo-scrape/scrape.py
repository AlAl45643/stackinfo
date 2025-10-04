from selenium.webdriver import FirefoxOptions
from selenium.webdriver import FirefoxService
from selenium.webdriver import Firefox
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
import os
import re
from datetime import datetime
import time

home_path = os.path.expanduser("~")
tor_directory = os.path.join(
    home_path, "src", "stackinfo", "src", "stackinfo-scrape", "tor-browser")
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
# firefox_options.add_argument("--headless")

tor_browser = Firefox(firefox_options, firefox_driver_service)


def wait_for_tor_connection(driver: Firefox):
    wait = WebDriverWait(driver, 200.0)
    wait.until(lambda _: driver.title == "")


def attr_value_exists(driver: Firefox, tag: str, atr: str, attr_value: str):
    try:
        elements = driver.find_elements(By.TAG_NAME, tag)
        for element in elements:
            attribute = element.get_attribute(atr)
            if attribute == attr_value:
                return True
        return False
    except StaleElementReferenceException:
        return False


def wait_for_attr_value(driver: Firefox, tag: str, atr: str, attr_value: str):
    wait = WebDriverWait(driver, 180.0)
    wait.until(lambda _: attr_value_exists(driver, tag, atr, attr_value))


with tor_browser:
    wait_for_tor_connection(tor_browser)
    tor_browser.get("https://att.wd1.myworkdayjobs.com/en-US/ATTCollege")
    wait_for_attr_value(tor_browser, "a", "data-automation-id", "jobTitle")
    elements = tor_browser.find_elements(By.TAG_NAME, "a")
    hrefs = []
    for element in elements:
        href = element.get_attribute("href")
        if re.search("/job/", href) is not None:
            hrefs.append(href)
    for href in hrefs:
        tor_browser.get(href)
        wait_for_attr_value(tor_browser, "div",
                            "data-automation-id", "job-posting-details")

