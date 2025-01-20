import re
import time
import datetime
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from call_status_monitor import get_telephony_call_info
from basicOperation import BaseOperations  # 导入 BaseOperations
from loadConfig import load_call_config

def normalize_phone_number(phone_number):
    phone_number = phone_number.strip()  # 去掉前后空格
    if phone_number.startswith("+"):
        phone_number = phone_number.replace(" ", "")  # 去掉号码中的空格
    return re.sub(r"[^\d+]", "", phone_number)  # 移除非数字和 "+" 符号


def prepare_for_dialing(driver):
    """准备拨号操作，确保配置文件包含最新的 SIM 卡信息"""
    print("更新设备中的 SIM 卡信息...")
    load_call_config(driver=driver, file_path="call_config.txt")  # 确保 driver 被传递

def log_call_to_txt(call_type, sim_name, start_time, duration, end_time):
    """记录通话信息到 txt 文件"""
    with open("call_logs.txt", "a", encoding="utf-8") as file:
        file.write(f"通话类型: {call_type}\n")
        file.write(f"SIM卡: {sim_name}\n")
        file.write(f"通话开始时间: {start_time.strftime('%H:%M:%S')}\n")
        file.write(f"通话结束时间: {end_time.strftime('%H:%M:%S')}\n")
        file.write(f"通话时长: {duration:.2f} 秒\n")
        file.write("-" * 30 + "\n")

def dial_number_with_sim(driver, number, sim_name, sim_info):
    """使用指定 SIM 卡拨号"""
    driver.execute_script("mobile: shell", {
        "command": "am",
        "args": ["start", "-a", "android.intent.action.CALL", "-d", f"tel:{number}"]
    })
    time.sleep(0.5)
    if check_sim_selection_popup(driver):
        select_sim_for_call(driver, sim_name, sim_info)
    else:
        print("SIM 选择界面未弹出，可能已使用默认 SIM 卡")

def check_sim_selection_popup(driver):
    """检查是否弹出 SIM 卡选择弹窗"""
    try:
        sim_popup = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Choose SIM for this call")')
        return sim_popup.is_displayed()
    except:
        return False

def select_sim_for_call(driver, sim_name, sim_info):
    """选择指定 SIM 卡拨号"""
    try:
        expected_operator = sim_info[sim_name]["Operator"].strip().lower()
        expected_number = normalize_phone_number(sim_info[sim_name]["Number"])

        # print(f"尝试选择 SIM 卡: {sim_name}, 运营商: {expected_operator}, 号码: {expected_number}")

        sim_options = driver.find_elements(AppiumBy.ID, "com.google.android.dialer:id/label")
        sim_numbers = driver.find_elements(AppiumBy.ID, "com.google.android.dialer:id/number")

        if not sim_options or not sim_numbers:
            print("未找到 SIM 卡选择元素，可能是定位问题。")
            return

        for option, number in zip(sim_options, sim_numbers):
            option_text = option.text.strip().lower()
            number_text = normalize_phone_number(number.text)

            # print(f"检测到 SIM 选项: 运营商={option_text}, 号码={number_text}")

            if expected_operator in option_text and expected_number == number_text:
                option.click()
                # print(f"成功选择 {sim_name} 进行拨号。")
                return

        print(f"未找到匹配的 SIM 卡: {sim_name} ({expected_operator}, {expected_number})")
    except Exception as e:
        print(f"选择 {sim_name} 失败: {e}")


def monitor_and_hang_up_call(driver, sim_index, sim_name, duration):
    """监控并挂断通话"""
    call_connected = False
    start_time = time.time()
    while not call_connected and time.time() - start_time < 30:
        call_info_sim1, call_info_sim2 = get_telephony_call_info(driver)
        call_connected = (sim_index == 0 and is_call_active(call_info_sim1)) or (sim_index == 1 and is_call_active(call_info_sim2))
        time.sleep(0.5)
    if call_connected:
        print("Call connected")
        time.sleep(duration)
        hang_up_call(driver)
        log_call_to_txt("拨号", sim_name, datetime.datetime.now(), duration, datetime.datetime.now())
    else:
        print("通话未接通")

def is_call_active(call_info):
    """检查通话是否已接通"""
    return call_info.get("mCallState") == 2 and call_info.get("mForegroundCallState") == 1

def hang_up_call(driver):
    """挂断电话"""
    try:
        driver.press_keycode(6)
        # print("电话已挂断")
    except Exception as e:
        print(f"挂断电话失败: {e}")

def run_call_test(driver, sim_name, dial_number):
    call_config = load_call_config()  # 加载配置文件
    sim_key_prefix = sim_name.replace("SIM", "SIM_")
    sim_operator = call_config.get(f"{sim_key_prefix}_OPERATOR")
    sim_number = call_config.get(f"{sim_key_prefix}_NUMBER")
    dial_duration = call_config.get("dial_duration", 15)

    if not sim_operator or not sim_number:
        print(f"配置文件中缺少 {sim_name} 的 SIM 信息: SIM_1_OPERATOR={sim_operator}, SIM_1_NUMBER={sim_number}")
        # print("请检查配置文件是否正确更新或重新运行 SIM 卡信息读取操作。")
        return
    sim_info = {
        sim_name: {
            "Operator": sim_operator,
            "Number": sim_number
        }
    }
    # print(sim_info)
    # print(f"{sim_name} 开始拨打 {dial_number}")
    dial_number_with_sim(driver, dial_number, sim_name, sim_info)
    monitor_and_hang_up_call(driver, 0 if sim_name == "SIM1" else 1, sim_name, dial_duration)
    # print(f"{sim_name} 拨号完成")



def __main__(driver):
    """
    主入口，运行拨号测试
    :param driver: Appium 驱动
    """
    # 如果需要读取SIM卡信息则去除标记符号
    # prepare_for_dialing(driver)
    time.sleep(0.3)
    call_config = load_call_config()
    sim_name = "SIM2"  # 默认使用 SIM1
    dial_number = call_config.get("dial_number1")  # 从配置中读取拨号号码

    if not dial_number:
        print("未在配置文件中找到拨号号码，终止测试")
        return
    run_call_test(driver, sim_name, dial_number)
    # print("拨号测试完成")


