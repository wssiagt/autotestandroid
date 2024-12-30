import time
import datetime
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from threading import Thread
from appium.options.android import UiAutomator2Options
from call_status_monitor import get_call_info, monitor_call_state
from switch_network_type import enter_data_setting, go_home, wake_up_screen

def get_sim_info(driver):
    go_home(driver)
    time.sleep(0.2)
    enter_data_setting(driver)
    time.sleep(0.5)
    sim_info = {}
    try:
        sim1_element = driver.find_element(AppiumBy.ID, "com.android.phone:id/sim_1")
        operator_name_sim1 = sim1_element.find_element(AppiumBy.ID, "com.android.phone:id/title").text
        sim_number_sim1 = sim1_element.find_element(AppiumBy.ID, "com.android.phone:id/summary").text
        sim_info["SIM1"] = {"Operator": operator_name_sim1, "Number": sim_number_sim1}
    except Exception as e:
        print(f"Error accessing SIM1: {e}")
    try:
        sim2_element = driver.find_element(AppiumBy.ID, "com.android.phone:id/sim_2")
        operator_name_sim2 = sim2_element.find_element(AppiumBy.ID, "com.android.phone:id/title").text
        sim_number_sim2 = sim2_element.find_element(AppiumBy.ID, "com.android.phone:id/summary").text
        sim_info["SIM2"] = {"Operator": operator_name_sim2, "Number": sim_number_sim2}
    except Exception as e:
        print(f"Error accessing SIM2: {e}")
    #print("Saved SIM info:", sim_info)
    return sim_info

def load_call_config(file_path="call_config.txt"):
    """加载拨号测试配置文件"""
    config = {}
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                if value.isdigit():
                    value = int(value)
                elif value.lower() in ("true", "false"):
                    value = value.lower() == "true"
                config[key] = value
            else:
                print(f"跳过无效行: {line}")
    return config

def log_call_to_txt(call_type, sim_name, start_time, duration, end_time):
    """记录通话信息到 txt 文件"""
    with open("call_logs.txt", "a", encoding="utf-8") as file:
        file.write(f"通话类型: {call_type}\n")
        file.write(f"SIM卡: {sim_name}\n")
        file.write(f"通话开始时间: {start_time.strftime('%H:%M:%S')}\n")
        file.write(f"通话结束时间: {end_time.strftime('%H:%M:%S')}\n")
        file.write(f"通话时长: {duration:.2f} 秒\n")
        file.write("-" * 30 + "\n")  # 分隔线

def dial_number_with_sim(driver, number, sim_name, sim_info):
    print(f"{sim_name} 拨打 {number} ...")
    driver.execute_script("mobile: shell", {
        "command": "am",
        "args": ["start", "-a", "android.intent.action.CALL", "-d", f"tel:{number}"]
    })
    time.sleep(0.5)
    sim_selection_displayed = check_sim_selection_popup(driver)
    if not sim_selection_displayed:
        print(datetime.datetime.now().strftime('%H:%M:%S'), "SIM 选择界面未弹出，可能已使用默认 SIM 卡")
        return
    try:
        expected_operator_name = sim_info[sim_name]["Operator"]
        sim_options = driver.find_elements(AppiumBy.ID, "com.google.android.dialer:id/label")
        for sim_option in sim_options:
            if expected_operator_name.lower() in sim_option.text.lower():
                sim_option.click()
                return
        print(f"未找到与 {sim_name} 匹配的运营商名称: {expected_operator_name}")
    except Exception as e:
        print(f"选择 {sim_name} 失败: {e}")

def check_sim_selection_popup(driver):
    try:
        sim_selection_popup = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Choose SIM for this call")')
        if sim_selection_popup.is_displayed():
            return True
    except:
        print("SIM 选择界面未弹出，跳过本次通话")
    return False

def monitor_and_hang_up_call(driver, sim_index, sim_name, duration, dial_number):
    call_connected = False
    start_time = time.time()
    connection_time = None
    while not call_connected and time.time() - start_time < 30:
        call_info_sim1, call_info_sim2 = get_call_info(driver)
        if sim_index == 0 and call_info_sim1.get("mCallState") == 2 and call_info_sim1["mForegroundCallState"] == 1:
            call_connected = True
            connection_time = time.time()
        elif sim_index == 1 and call_info_sim2.get("mCallState") == 2 and call_info_sim2["mForegroundCallState"] == 1:
            call_connected = True
            connection_time = time.time()
        time.sleep(0.5)
    if call_connected:
        print("Call up")
        time.sleep(duration)
        hang_up_call(driver)
        actual_duration = time.time() - connection_time
        is_exception = actual_duration < duration
        log_call_to_txt("拨号", sim_name, datetime.datetime.now(), actual_duration, datetime.datetime.now())
    else:
        print("通话未接通，超时退出")
        log_call_to_txt("拨号", sim_name, datetime.datetime.now(), 0, datetime.datetime.now())

def hang_up_call(driver):
    try:
        driver.press_keycode(6)  # KEYCODE_ENDCALL
        print("电话已挂断")
    except Exception as e:
        print(f"挂断电话失败: {e}")

def run_call_tests(driver):
    call_config = load_call_config()
    dial_number = call_config["dial_number"]
    dial_times = call_config["dial_times"]
    dial_duration = call_config["dial_duration"]
    wait_time = call_config["wait_time"]

    for i in range(dial_times):
        print(f"\n开始第 {i + 1} 轮通话...")

        print("使用 SIM1 拨号...")
        start_time_sim1 = datetime.datetime.now()
        dial_number_with_sim(driver, dial_number, sim_name="SIM1")
        monitor_and_hang_up_call(driver, 0, "SIM1", dial_duration, dial_number)

        time.sleep(wait_time)

        print("使用 SIM2 拨号...")
        start_time_sim2 = datetime.datetime.now()
        dial_number_with_sim(driver, dial_number, sim_name="SIM2")
        monitor_and_hang_up_call(driver, 1, "SIM2", dial_duration, dial_number)

        time.sleep(wait_time)
        print(f"第 {i + 1} 轮通话结束\n" + "-" * 35)
    print("所有通话测试完成")
