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
        
def enter_prefer_network(driver):
    try:
        find_and_click_element(driver, "Preferred network type")
        time.sleep(0.2)
    except Exception as e:
        print('Error: Preferred network type icon not found')
        
def go_home(driver):
    try:
        driver.press_keycode(3)  # 3 是 KEYCODE_HOME
        time.sleep(0.1)
    except Exception as e:
        print(f"返回主屏幕失败: {e}")

def open_sim_network_settings(driver, sim_label):
    wake_up_screen(driver)
    enter_data_setting(driver)
    time.sleep(0.3)
    try:
        driver.find_element(AppiumBy.ID, sim_label).click()
        time.sleep(0.2)
    except Exception as e:
        print(f"Error in open_sim_network_settings: {e}")

def select_preferred_network_type(driver, target_keyword):
    """
    在 UI 中搜索所有元素，找到包含目标关键字或其同义关键字（如 4G 或 LTE）的元素并点击。
    """
    synonyms = {
        "4G": ["4G", "LTE"],
        "LTE": ["4G", "LTE"],
        "5G": ["5G"]
    }
    try:
        elements = driver.find_elements(AppiumBy.XPATH, "//*[@text]")
        for element in elements:
            text = element.text
            if text:
                for synonym in synonyms.get(target_keyword.upper(), [target_keyword]):
                    if synonym in text:
                        element.click()
                        print(f"Successfully selected network type: {text}")
                        return
        print(f"Error: Element with text containing '{target_keyword}' or its synonyms not found.")
    except Exception as e:
        print(f"Error selecting network type containing '{target_keyword}': {e}")

def validate_network_registration(target_network):
    """
    验证设备是否已注册到目标网络。
    根据 mTelephonyDisplayInfo 的 network 和 overrideNetwork 判断网络类型。
    """
    try:
        result = subprocess.run(["adb", "shell", "dumpsys", "telephony.registry"], capture_output=True, text=True)
        if result.returncode != 0:
            print("Error: Failed to fetch network state.")
            return False

        output = result.stdout.lower()
        if "mtelephonydisplayinfo" not in output:
            print("Error: TelephonyDisplayInfo not found in output.")
            return False

        lines = output.splitlines()
        # print(lines)
        for line in lines:
            if "mtelephonydisplayinfo" in line:
                if "5g" in target_network.lower() and "network=lte" in line and "overridenetwork=nr_nsa" in line:
                    print("Validation successful: Device is registered on 5G NSA network.")
                    return True
                elif "4g" in target_network.lower() and "network=lte" in line and "overridenetwork=none" in line:
                    print("Validation successful: Device is registered on 4G network.")
                    return True
                elif "3g" in target_network.lower() and "network=wcdma" in line:
                    print("Validation successful: Device is registered on 3G network.")
                    return True
                elif "2g" in target_network.lower() and "network=edge" in line:
                    print("Validation successful: Device is registered on 2G network.")
                    return True
        print(f"Validation failed: Device is not registered on {target_network} network.")
        return False
    except Exception as e:
        print(f"Error validating network registration: {e}")
        return False

def switch_network_type(driver, sim_slot, target_network):
    wake_up_screen(driver)
    target_sim_id = "com.android.phone:id/sim_1" if sim_slot == "SIM1" else "com.android.phone:id/sim_2"
    open_sim_network_settings(driver, target_sim_id)
    enter_prefer_network(driver)
    select_preferred_network_type(driver, target_network)
    print(f"{sim_slot} network switch to {target_network} done")

def main(sim_slot, network_type):
    if sim_slot.upper() not in ["SIM1", "SIM2"]:
        print("Invalid SIM slot. Please specify either 'SIM1' or 'SIM2'.")
        return
    switch_network_type(driver, sim_slot.upper(), network_type)
    time.sleep(15)
    if validate_network_registration(network_type):
        print("Network registration validated successfully.")
    else:
        print("Network registration validation failed.")
    driver.quit()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script_name.py <SIM1/SIM2> <Network Type>")
        sys.exit(1)

    sim_slot = sys.argv[1]
    network_type = sys.argv[2]
    main(sim_slot, network_type)
