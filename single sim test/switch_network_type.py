import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from mock_click import find_and_click_element

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
        time.sleep(0.3)
    except Exception as e:
        print(f"Error in enter_data_setting: {e}")
        print('Error: settings icon not found')
        return
    try:
        find_and_click_element(driver, "Mobile networks")
        time.sleep(0.3)
    except Exception as e:
        print(f"Error in enter_data_setting: {e}")

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
    driver.find_element(AppiumBy.ID, sim_label).click()
    time.sleep(0.3)

def get_all_network_types(driver):
    wake_up_screen(driver)
    find_and_click_element(driver, "Preferred network type")
    time.sleep(0.3)
    network_types_dict = {}
    elements = driver.find_elements(AppiumBy.XPATH, "//*")
    for element in elements:
        text = element.text
        if text:
            if "4G" in text or "LTE" in text:
                network_types_dict["4G/LTE"] = element
            elif "Prefer" in text and text != "Preferred network type":
                network_types_dict[text] = element
    return network_types_dict

def select_preferred_network_type(network_type_text):
    network_types_dict = get_all_network_types()
    target_network_type = "4G/LTE" if network_type_text.lower() in ["4g", "lte"] else network_type_text
    if target_network_type in network_types_dict:
        find_and_click_element(driver, network_types_dict[target_network_type].text)
        print(f"Successfully selected network type: {target_network_type}")
    else:
        print(f"Error: Target network type '{network_type_text}' not found.")

def switch_network_types(driver, network_types, target_network):
    if target_network.lower() in ["4g", "lte"]:
        target_network = "4G/LTE"
    for network_type in network_types:
        if target_network in network_type:
            print("Start SIM1 network switch")
            open_sim_network_settings(driver, "com.android.phone:id/sim_1")
            select_preferred_network_type(network_type)
            print("SIM1 network switch done")
            #time.sleep(0.3)
            #open_sim_network_settings(driver, "com.android.phone:id/sim_2")
            #select_preferred_network_type(network_type)
            #print("SIM2 network switch done")

def main():
    open_sim_network_settings("com.android.phone:id/sim_1")
    network_types = get_all_network_types()
    return network_types

def test_network_switch(net_type):
    network_types = main()
    if network_types:
        switch_network_types(driver, network_types, net_type)

if __name__ == "__main__":
    test_network_switch("LTE")