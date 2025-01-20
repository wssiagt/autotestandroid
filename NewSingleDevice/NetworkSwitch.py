from basicOperation import BaseOperations
from appium.webdriver.common.appiumby import AppiumBy
from voltetest import volte_main as volte
import time

class NetworkSwitcher:
    def __init__(self, driver):
        self.driver = driver
        self.base_ops = BaseOperations(driver)

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
                            # print(f"Successfully selected network type: {text}")
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
        # 处理 VoLTE 设置
        if "4g" in target_network.lower() or "5g" in target_network.lower():
            action = "ON" if "volte" in target_network.lower() else "OFF"
            volte(self.driver, sim_slot, action)