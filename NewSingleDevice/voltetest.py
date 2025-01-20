import time
from appium.webdriver.common.appiumby import AppiumBy
from mock_click import find_and_click_element
from basicOperation import BaseOperations  # 导入新的基础操作模块

def open_sim_network_settings(driver, sim_label):
    """打开 SIM 网络设置页面"""
    base_ops = BaseOperations(driver)  # 创建 BaseOperations 实例
    base_ops.wake_up_screen()
    base_ops.go_home()
    base_ops.enter_data_setting()
    time.sleep(0.3)
    driver.find_element(AppiumBy.ID, sim_label).click()
    time.sleep(0.2)

def launch_and_input_dialer_code(driver, secret_code):
    """
    启动拨号键盘并输入隐藏代码。
    """
    try:
        # print("Launching dialer application...")
        driver.execute_script('mobile: shell', {
            'command': 'am',
            'args': ['start', '-a', 'android.intent.action.DIAL'],
            'includeStderr': True
        })
        time.sleep(0.3)  # 等待拨号界面加载

        # print("Inputting secret code...")
        try:
            driver.find_element("id", "com.google.android.dialer:id/digits").click()
        except:
            # print(f"Error focusing input field with 'Phone Number': {e}, trying alternative approach.")
            find_and_click_element(driver, "Phone Number")  # 确保点击聚焦输入框
        time.sleep(0.3)
        driver.set_clipboard_text(secret_code)  # 设置剪贴板内容
        print(f"Clipboard set with secret code: {secret_code}")
        time.sleep(0.2)
        driver.execute_script('mobile: shell', {
            'command': 'input',
            'args': ['text', secret_code]
        })
        # print(f"Secret code '{secret_code}' pasted successfully.")
        time.sleep(1)  # 等待代码触发
    except Exception as e:
        print(f"Error during launch and input of secret code: {e}")

# def check_and_toggle_volte(driver, action, sim_label):
    # """
    # 检查并根据指定操作启用或禁用 VoLTE，优化了 CheckBox 定位逻辑。
    # """
    # base_ops = BaseOperations(driver)  # 创建 BaseOperations 实例
    # # open_sim_network_settings(driver, sim_label)
    # for attempt in range(2):  # 尝试两次，第二次触发 secret code
        # try:
            # print(f"Attempt {attempt + 1}: Checking for VoLTE/4G call option...")
            # driver.implicitly_wait(5)

            # # 定位到 VoLTE 文本
            # elements = driver.find_elements(AppiumBy.XPATH, "//*[contains(@text, 'Use VoLTE') or contains(@text, 'Use 4G call')]")
            # if elements:
                # element = elements[0]  # 假设第一个匹配的元素是目标元素
                # print("VoLTE call option found.")
                # try:
                    # # 使用更精确的 XPath 定位 CheckBox
                    # checkbox_xpath = "(//android.widget.CheckBox[@resource-id='android:id/checkbox'])[2]"
                    # checkbox = driver.find_element(AppiumBy.XPATH, checkbox_xpath)

                    # # 检查 CheckBox 的当前状态
                    # is_checked = checkbox.get_attribute("checked") == "true"
                    # print(f"CheckBox found. Current state: {'enabled' if is_checked else 'disabled'}")

                    # # 根据操作切换状态
                    # if action.lower() == "on" and not is_checked:
                        # print("Turning VoLTE ON.")
                        # checkbox.click()
                    # elif action.lower() == "off" and is_checked:
                        # print("Turning VoLTE OFF.")
                        # checkbox.click()
                    # else:
                        # print(f"VoLTE is already {'enabled' if is_checked else 'disabled'}. No action needed.")
                # except Exception as e:
                    # print(f"Error interacting with CheckBox: {e}")
                # return
            # else:
                # print("VoLTE/4G call option not found.")
                # if attempt == 0:  # 第一次尝试失败，触发 secret code
                    # print("Triggering secret code to unlock VoLTE/4G call settings...")
                    # launch_and_input_dialer_code(driver, "*#*#86583#*#*")
                    # time.sleep(1)  # 等待设置刷新
                    # # 重新导航到 SIM 网络设置页面
                    # open_sim_network_settings(driver, sim_label)
        # except Exception as e:
            # print(f"Error enabling VoLTE/4G call: {e}")
    # print("Error: VoLTE option could not be enabled or disabled.")


def check_and_toggle_volte(driver, action, sim_label):
    """
    检查并根据指定操作启用或禁用 VoLTE，优化了 CheckBox 定位逻辑。
    """
    base_ops = BaseOperations(driver)  # 创建 BaseOperations 实例
    # open_sim_network_settings(driver, sim_label)
    for attempt in range(2):  # 尝试两次，第二次触发 secret code
        try:
            # print(f"Attempt {attempt + 1}: Checking for VoLTE/4G call option...")
            driver.implicitly_wait(1)

            # 检索是否存在包含 SA 的元素
            sa_elements = driver.find_elements(AppiumBy.XPATH, "//*[contains(@text, 'SA')]")
            use2g_elements = driver.find_elements(AppiumBy.XPATH, "//*[contains(@text, 'use of 2G')]")
            if sa_elements or use2g_elements:
                # print("Found element containing 'SA' or 'Allow 2G'.")
                checkbox_xpath = "(//android.widget.CheckBox[@resource-id='android:id/checkbox'])[3]"
            else:
                # print("No element containing 'SA' found.")
                checkbox_xpath = "(//android.widget.CheckBox[@resource-id='android:id/checkbox'])[2]"

            # 定位到 VoLTE 文本
            elements = driver.find_elements(AppiumBy.XPATH, "//*[contains(@text, 'Use VoLTE') or contains(@text, 'Use 4G call')]")
            if elements:
                element = elements[0]  # 假设第一个匹配的元素是目标元素
                #print("VoLTE call option found.")
                try:
                    # 定位 CheckBox
                    checkbox = driver.find_element(AppiumBy.XPATH, checkbox_xpath)

                    # 检查 CheckBox 的当前状态
                    is_checked = checkbox.get_attribute("checked") == "true"
                    # print(f"CheckBox found. Current state: {'enabled' if is_checked else 'disabled'}")

                    # 根据操作切换状态
                    if action.lower() == "on" and not is_checked:
                        print("Turning VoLTE ON.")
                        checkbox.click()
                    elif action.lower() == "off" and is_checked:
                        print("Turning VoLTE OFF.")
                        checkbox.click()
                    else:
                        pass
                        # print(f"VoLTE is already {'enabled' if is_checked else 'disabled'}. No action needed.")
                except Exception as e:
                    print(f"Error interacting with CheckBox: {e}")
                return
            else:
                print("VoLTE/4G call option not found.")
                if attempt == 0:  # 第一次尝试失败，触发 secret code
                    # print("Triggering secret code to unlock VoLTE/4G call settings...")
                    launch_and_input_dialer_code(driver, "*#*#86583#*#*")
                    time.sleep(1)  # 等待设置刷新
                    # 重新导航到 SIM 网络设置页面
                    open_sim_network_settings(driver, sim_label)
        except Exception as e:
            print(f"Error enabling VoLTE/4G call: {e}")
    print("Error: VoLTE option could not be enabled or disabled.")
    
    
def volte_main(driver, sim_slot, action):
    """
    主函数入口，指定 SIM 卡槽和 VoLTE 操作。
    """
    sim_label = "com.android.phone:id/sim_1" if sim_slot.upper() == "SIM1" else "com.android.phone:id/sim_2"
    # open_sim_network_settings(driver, sim_label)
    check_and_toggle_volte(driver, action, sim_label)