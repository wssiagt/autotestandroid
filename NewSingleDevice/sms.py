import time
import sys
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from mock_click import find_and_click_element, find_and_click_exact
        
def initialize_driver():
    options = UiAutomator2Options()
    options.platform_name = 'Android'
    options.device_name = 'DUT'
    driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
    time.sleep(1)
    return driver

def wake_up_screen(driver):
    try:
        driver.press_keycode(224)  # Power button to wake the screen
        time.sleep(0.3)
    except Exception as e:
        print(f"Error waking up screen: {e}")

def open_sms_app_directly(driver, phone_number, message):
    try:
        print("Sending SMS...")
        driver.execute_script(
            "mobile: shell",
            {
                "command": "am",
                "args": [
                    "start",
                    "-a", "android.intent.action.SENDTO",
                    "-d", f"sms:{phone_number}",
                    "--es", "sms_body", f'"{message}"',
                    "--ez", "exit_on_sent", "true"
                ]
            }
        )
        time.sleep(2)
    except Exception as e:
        print(f"Error opening SMS app: {e}")

def select_sim(driver, target_sim):
    try:
        print("Checking current SIM selection...")
        driver.implicitly_wait(2)
        wake_up_screen(driver)
        sim_selector = driver.find_element(AppiumBy.XPATH, "//*[contains(@content-desc, 'Select SIM')]")
        time.sleep(0.2)
        current_sim = sim_selector.get_attribute("content-desc")
        if target_sim == "SIM1" and "[1/2]" not in current_sim:
            print("Switching to SIM1...")
            sim_selector.click()
            find_and_click_exact(driver, "1")
            time.sleep(1)
        elif target_sim == "SIM2" and "[2/2]" not in current_sim:
            print("Switching to SIM2...")
            sim_selector.click()
            find_and_click_exact(driver, "2")
            time.sleep(1)
        else:
            print(f"Target SIM ({target_sim}) is already selected.")
    except Exception as e:
        print(f"Error selecting SIM: {e}")
        debug_ui_structure(driver)

def debug_ui_structure(driver):
    try:
        elements = driver.find_elements(AppiumBy.XPATH, "//*[@content-desc]")
        for elem in elements:
            print(f"Element content-desc: {elem.get_attribute('content-desc')}")
    except Exception as e:
        print(f"Error debugging UI structure: {e}")

def send_sms(driver):
    try:
        driver.implicitly_wait(1)
        send_button = driver.find_element(AppiumBy.XPATH, "//*[contains(@text, 'Send') or contains(@content-desc, 'Send')]")
        send_button.click()
        print("Message sent successfully.")
    except Exception as e:
        print(f"Error clicking send button: {e}")
        debug_ui_structure(driver)

def main():
    if len(sys.argv) != 4:
        print("Usage: python sms.py <phone_number> <message> <SIM1/SIM2>")
        sys.exit(1)

    phone_number = sys.argv[1]
    message = sys.argv[2]
    target_sim = sys.argv[3].upper()

    if target_sim not in ["SIM1", "SIM2"]:
        print("Invalid SIM selection. Use SIM1 or SIM2.")
        sys.exit(1)

    driver = initialize_driver()
    wake_up_screen(driver)

    for i in range(2):  # 发送两次短信
        print(f"Sending SMS #{i + 1}...")
        open_sms_app_directly(driver, phone_number, message)
        time.sleep(0.2)
        select_sim(driver, target_sim)
        time.sleep(0.5)
        send_sms(driver)
        if i < 1:  # 只在第一次发送后等待
            print("Waiting 3 seconds before sending the next message...")
            time.sleep(3)

    driver.quit()

if __name__ == "__main__":
    main()