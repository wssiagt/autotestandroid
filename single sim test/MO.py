import time
import datetime
from appium import webdriver
from mock_click import find_and_click_element
from appium.webdriver.common.appiumby import AppiumBy
from switch_network_type import enter_data_setting, go_home, wake_up_screen
from appium.options.android import UiAutomator2Options
from call_status_monitor import get_call_info, monitor_call_state

def record_call_data(sim_name, target_number, start_time, duration, is_exception):
    end_time = time.time()
    actual_duration = end_time - start_time
    end_time_formatted = time.strftime('%H:%M:%S', time.localtime(end_time))
    start_time_formatted = time.strftime('%H:%M:%S', time.localtime(start_time))
    record = (
        f"{sim_name}\n"
        f"目标号码: {target_number}\n"
        f"开始: {start_time_formatted}\n"
        f"结束: {end_time_formatted}\n"
        f"通话时长: {actual_duration:.2f} 秒\n"
        f"异常: {'#####是#####' if is_exception else '否'}\n"
        "-----------------------------------\n"
    )
    with open("call_log.txt", "a", encoding="utf-8") as file:
        file.write(record)
        
def dial_number_with_sim(driver, number, sim_name):
    print(f"{sim_name} 拨打 {number} ...")
    # subprocess.run(f"adb shell am start -a android.intent.action.CALL -d tel:{number}", shell=True)
    driver.execute_script("mobile: shell", {
            "command": "am",
            "args": ["start", "-a", "android.intent.action.CALL", "-d", f"tel:{number}"]
        })
    time.sleep(0.5)

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
        if sim_index == 0 and call_info_sim1 and call_info_sim1["mCallState"] == 2 and call_info_sim1["mForegroundCallState"] == 1:
            call_connected = True
            connection_time = time.time()
        elif sim_index == 1 and call_info_sim2 and call_info_sim2["mCallState"] == 2 and call_info_sim2["mForegroundCallState"] == 1:
            call_connected = True
            connection_time = time.time()
        time.sleep(1)
    if call_connected:
        time.sleep(duration)
        hang_up_call(driver)
        actual_duration = time.time() - connection_time
        is_exception = actual_duration < duration
        record_call_data(sim_name, dial_number, connection_time, duration, is_exception)
        go_back(driver)
    else:
        print(datetime.datetime.now().strftime('%H:%M:%S'), "通话未接通，超时退出")
        record_call_data(sim_name, dial_number, start_time, 0, is_exception=True)
        time.sleep(1)
        hang_up_call(driver)
        go_back(driver)
        
def hang_up_call(driver):
    try:
        driver.press_keycode(6)  # 6 是 KEYCODE_ENDCALL
        print("电话已挂断")
    except Exception as e:
        print(f"挂断电话失败: {e}")
    
def go_back(driver):
    try:
        time.sleep(0.2)
        driver.press_keycode(4)  # 4 是 KEYCODE_BACK
        time.sleep(0.2)
        driver.press_keycode(4)  # 再次返回上一层
        print("已返回两层")
    except Exception as e:
        print(f"返回操作失败: {e}")