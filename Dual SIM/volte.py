import time
import sys
import subprocess
import requests
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from mock_click import find_and_click_element

options = UiAutomator2Options()
options.platform_name = 'Android'
options.device_name = 'DUT'
driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
time.sleep(1)

def wake_up_screen(driver):
    try:
        driver.press_keycode(224)
        time.sleep(0.3)
    except Exception as e:
        print(f"唤醒屏幕失败: {e}")

def enter_data_setting(driver):
    wake_up_screen(driver)
    go_home(driver)
    try:
        find_and_click_element(driver, "Settings")
        time.sleep(0.2)
    except Exception as e:
        print('Error: settings icon not found')
        return
    try:
        find_and_click_element(driver, "Mobile networks")
        time.sleep(0.2)
    except Exception as e:
        print('Error: Mobile networks icon not found')
        
def open_sim_network_settings(driver, sim_label):
    wake_up_screen(driver)
    enter_data_setting(driver)
    time.sleep(0.3)
    try:
        driver.find_element(AppiumBy.ID, sim_label).click()
        time.sleep(0.2)
    except Exception as e:
        print(f"Error in open_sim_network_settings: {e}")

def check_and_toggle_volte(driver, action):
    """检查并根据指定操作启用或禁用 VoLTE"""
    for attempt in range(2):  # 尝试两次，第二次触发 secret code
        try:
            print(f"Attempt {attempt + 1}: Checking for VoLTE/4G call option...")
            driver.implicitly_wait(5)
            elements = driver.find_elements(AppiumBy.XPATH, "//*[contains(@text, 'Use VoLTE') or contains(@text, 'Use 4G call')]")
            
            if elements:
                element = elements[0]
                print("VoLTE call option found.")
                try:
                    sibling_layout = driver.find_element(AppiumBy.XPATH, "//*[contains(@text, 'Use VoLTE')]/following-sibling::*[@resource-id='android:id/widget_frame']")
                    checkbox = sibling_layout.find_element(AppiumBy.CLASS_NAME, "android.widget.CheckBox")
                    is_checked = checkbox.get_attribute("checked") == "true"

                    if action.lower() == "on" and not is_checked:
                        print("Turning VoLTE ON.")
                        sibling_layout.click()
                    elif action.lower() == "off" and is_checked:
                        print("Turning VoLTE OFF.")
                        sibling_layout.click()
                    else:
                        print(f"VoLTE is already {'enabled' if is_checked else 'disabled'}. No action needed.")
                except Exception as e:
                    print(f"Error interacting with checkbox or parent container: {e}")
                return
            else:
                print("VoLTE/4G call option not found.")
                if attempt == 0:  # 触发 secret code
                    print("Triggering secret code to unlock VoLTE/4G call settings...")
                    driver.execute_script(
                        'mobile: shell',
                        {'command': 'am broadcast -a android.provider.Telephony.SECRET_CODE -d android_secret_code://86583'}
                    )
                    time.sleep(5)  # 等待设置刷新
        except Exception as e:
            print(f"Error enabling VoLTE/4G call: {e}")
    print("Error: VoLTE option could not be enabled or disabled.")

def go_home(driver):
    try:
        driver.press_keycode(3)  # 3 是 KEYCODE_HOME
        time.sleep(0.1)
    except Exception as e:
        print(f"返回主屏幕失败: {e}")

def main():
    # 如果是 Jupyter Notebook，用硬编码参数代替
    if 'ipykernel' in sys.modules:
        sys.argv = ['script_name.py', 'SIM1 OFF']
    
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <SIM1/SIM2 On/Off>")
        sys.exit(1)

    input_arg = sys.argv[1].split()
    if len(input_arg) != 2 or input_arg[0] not in ["SIM1", "SIM2"] or input_arg[1].lower() not in ["on", "off"]:
        print("Invalid argument. Use format: SIM1 On or SIM2 Off.")
        sys.exit(1)

    sim_slot = "com.android.phone:id/sim_1" if input_arg[0] == "SIM1" else "com.android.phone:id/sim_2"
    action = input_arg[1].lower()

    open_sim_network_settings(driver, sim_slot)
    check_and_toggle_volte(driver, action)
    driver.quit()

if __name__ == "__main__":
    main()
