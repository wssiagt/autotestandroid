import time
import subprocess
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException

def find_and_click_element(driver, text):
    try:
        time.sleep(0.3)
        element = driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().textContains("{text}")'
        )
        if element.get_attribute("clickable") == "true":
            element.click()
        else:
            ancestor_element = driver.find_element(AppiumBy.XPATH,f"//*[contains(@text, '{text}')]/ancestor::*[@clickable='true']")
            ancestor_element.click()
    except NoSuchElementException:
        print(f"Error: Element with text '{text}' not found using both methods.")