from selenium.webdriver import FirefoxOptions
from selenium.webdriver import FirefoxService
# from undetected_geckodriver import Firefox
from selenium.webdriver import Firefox
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException


import os


firefox = Firefox()


# def wait_for_tor_connection(driver: Firefox):
#     wait = WebDriverWait(driver, 180)
#     wait.until(lambda _: driver.title == "")


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

# with firefox:
#     firefox.get(
#         "hiring.cafe")
#     wait_for_site_content(firefox)


firefox.get("hiring.cafe")
