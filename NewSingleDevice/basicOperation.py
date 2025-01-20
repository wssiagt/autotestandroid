import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException  # 修复未导入的问题

class BaseOperations:
    def __init__(self, driver):
        self.driver = driver

    def wake_up_screen(self):
        try:
            self.driver.press_keycode(224)  # 224 is the keycode for POWER
            time.sleep(0.3)
        except Exception as e:
            print(f"Failed to wake up screen: {e}")

    def go_home(self):
        try:
            self.driver.press_keycode(3)  # 3 is the keycode for HOME
            time.sleep(0.3)
        except Exception as e:
            print(f"Failed to return to home screen: {e}")

    def enter_data_setting(self):
        self.wake_up_screen()
        self.go_home()
        try:
            self.find_and_click_element("Settings")
            time.sleep(0.3)
        except Exception as e:
            print('Error: Settings icon not found')
            return
        try:
            self.find_and_click_element("Mobile networks")
            time.sleep(0.3)
        except Exception as e:
            print('Error: Mobile networks icon not found')
            
    def enter_prefer_network(self):
        try:
            self.find_and_click_element("Preferred network type")
            time.sleep(0.3)
        except Exception as e:
            print('Error: Preferred network type icon not found')
            
    def find_and_click_element(self, text):
        try:
            time.sleep(0.3)
            element = self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().textContains("{text}")'
            )
            if element.get_attribute("clickable") == "true":
                element.click()
            else:
                ancestor_element = self.driver.find_element(
                    AppiumBy.XPATH,
                    f"//*[contains(@text, '{text}')]/ancestor::*[@clickable='true']"
                )
                ancestor_element.click()
        except NoSuchElementException:
            print(f"Error: Element with text '{text}' not found using both methods.")
        except Exception as e:
            print(f"Error: {e}")
        
    def find_and_click_exact(self, text):
        try:
            time.sleep(0.3)
            element = self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().text("{text}")'
            )
            if element.get_attribute("clickable") == "true":
                element.click()
            else:
                ancestor_element = self.driver.find_element(
                    AppiumBy.XPATH,
                    f"//*[@text='{text}']/ancestor::*[@clickable='true']"
                )
                ancestor_element.click()
        except NoSuchElementException:
            print(f"Error: Element with text '{text}' not found using both methods.")
        except Exception as e:
            print(f"Error: {e}")
            
    def launch_and_input_dialer_code(self, secret_code):
        """
        启动拨号键盘并输入隐藏代码。
        """
        try:
            print("Launching dialer application...")
            self.driver.execute_script('mobile: shell', {
                'command': 'am',
                'args': ['start', '-a', 'android.intent.action.DIAL'],
                'includeStderr': True
            })
            time.sleep(0.3)  # 等待拨号界面加载

            print("Inputting secret code...")
            find_and_click_element(driver, "Phone Number")  # 确保点击聚焦输入框
            time.sleep(0.3)
            self.driver.set_clipboard_text(secret_code)  # 设置剪贴板内容
            print(f"Clipboard set with secret code: {secret_code}")
            time.sleep(0.2)
            self.driver.execute_script('mobile: shell', {
                'command': 'input',
                'args': ['text', secret_code]
            })
            print(f"Secret code '{secret_code}' pasted successfully.")
            time.sleep(1)  # 等待代码触发
        except Exception as e:
            print(f"Error during launch and input of secret code: {e}")

    def execute_adb_command(self, command):
        self.driver.execute_script("mobile: shell", {
            'command': command,
            'args': [],
            'includeStderr': True,
            'timeout': 5000
        })

    def enable_auto_answer(self):
        pass
    
    def toggle_airplane_mode_via_settings(self, enable):
        try:
            # 打开飞行模式设置页面
            self.execute_adb_command("am start -a android.settings.AIRPLANE_MODE_SETTINGS")
            time.sleep(0.5)  # 等待设置页面加载

            # 查找飞行模式开关并根据需要切换
            if enable:
                self.find_and_click_element("Aeroplane mode")
                # print("Airplane mode enabled.")
            else:
                self.find_and_click_element("Aeroplane mode")
                # print("Airplane mode disabled.")

        except NoSuchElementException:
            print("Error: Airplane mode toggle not found.")
        except Exception as e:
            print(f"Error setting airplane mode: {e}")