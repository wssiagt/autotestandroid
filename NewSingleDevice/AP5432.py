import time
import sys
import subprocess
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from voltetest import volte_main as volte
from basicOperation import BaseOperations
from NetworkValidation import NetworkValidator

class NetworkSwitcher:
    def __init__(self, driver):
        self.driver = driver
        self.base_ops = BaseOperations(driver)
        self.network_validator = NetworkValidator(driver)

    def open_sim_network_settings(self, sim_label):
        """打开 SIM 网络设置页面"""
        self.base_ops.wake_up_screen()
        self.base_ops.enter_data_setting()
        time.sleep(0.3)
        try:
            self.driver.find_element(AppiumBy.ID, sim_label).click()
            time.sleep(0.2)
        except Exception as e:
            print(f"Error in open_sim_network_settings: {e}")

    def select_preferred_network_type(self, target_keyword):
        """选择首选网络类型"""
        target_keyword_short = target_keyword[:2]  # 仅对网络类型提取前两个字符
        synonyms = {
            "4G": ["4G", "LTE"],
            "LTE": ["4G", "LTE"],
            "5G": ["5G"]
        }
        try:
            elements = self.driver.find_elements(AppiumBy.XPATH, "//*[@text]")
            for element in elements:
                text = element.text
                if text:
                    for synonym in synonyms.get(target_keyword_short.upper(), [target_keyword_short]):
                        if synonym in text:
                            element.click()
                            print(f"Successfully selected network type: {text}")
                            return
            print(f"Error: Element with text containing '{target_keyword_short}' or its synonyms not found.")
        except Exception as e:
            print(f"Error selecting network type containing '{target_keyword_short}': {e}")

    def switch_network_type(self, sim_slot, target_network):
        """切换 SIM 网络类型"""
        target_sim_id = "com.android.phone:id/sim_1" if sim_slot.upper() == "SIM1" else "com.android.phone:id/sim_2"
        self.open_sim_network_settings(target_sim_id)
        self.base_ops.enter_prefer_network()  # 进入 Preferred network type
        self.select_preferred_network_type(target_network)
        print(f"Switched network type to {target_network}")

        # 处理 VoLTE 设置
        # if "4g" in target_network.lower() or "5g" in target_network.lower():
            # action = "ON" if "volte" in target_network.lower() else "OFF"
            # volte(self.driver, sim_slot, action)

    def test_ping(self):
        """测试网络连通性"""
        host = "8.8.8.8"  # Google DNS
        try:
            result = subprocess.run(["adb", "shell", "ping", "-c", "4", host], capture_output=True, text=True)
            if "0% packet loss" in result.stdout:
                print("Ping Test Successful")
            else:
                print("Ping Test Failed")
            print(result.stdout)
        except Exception as e:
            print(f"Ping Test Error: {e}")

    def validate_network_registration(self, sim_slot, target_network):
        """验证网络注册是否成功"""
        return self.network_validator.ensure_network_registration(sim_slot, target_network)


def main(sim_slot, network_types_duty):
    options = UiAutomator2Options()
    options.platform_name = 'Android'
    options.device_name = 'DUT'
    driver = webdriver.Remote('http://127.0.0.1:4723', options=options)

    try:
        switcher = NetworkSwitcher(driver)
        if sim_slot.upper() not in ["SIM1", "SIM2"]:
            print("Invalid SIM slot. Please specify either 'SIM1' or 'SIM2'.")
            return

        base_ops = BaseOperations(driver)
        base_ops.toggle_airplane_mode_via_settings(enable=True)  # Enable airplane mode
        time.sleep(1)
        base_ops.toggle_airplane_mode_via_settings(enable=False)  # Disable airplane mode

        for network_type in network_types_duty:
            print(f"Processing network type: {network_type}")
            switcher.switch_network_type(sim_slot.upper(), network_type)
            time.sleep(3)

            if switcher.validate_network_registration(sim_slot.upper(), network_type):
                if network_type == "2G" or network_type == "3G":
                    # print(f"Network registration validated successfully for {network_type}.")
                    time.sleep(6)
                    switcher.test_ping()
                else:
                    time.sleep(3)
                    switcher.test_ping()
            else:
                print(f"Network registration validation failed for {network_type}.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script_name.py <SIM1/SIM2> <network_types_duty as comma-separated values>")
        sys.exit(1)

    sim_slot = sys.argv[1]
    network_types_duty = sys.argv[2].split(",")  # Split the network types by comma

    main(sim_slot, network_types_duty)
