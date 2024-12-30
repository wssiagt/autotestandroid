from appium.options.android import UiAutomator2Options
from appium import webdriver
import time
from datetime import datetime
from time import sleep
from appium.webdriver.common.appiumby import AppiumBy
from call_status_monitor import register_callback, monitor_call_state

def log_call_to_txt(call_type, sim_index, start_time, duration, end_time):
    """记录通话信息到 txt 文件"""
    with open("incoming_call_logs.txt", "a", encoding="utf-8") as file:
        file.write(f"通话类型: {call_type}\n")
        file.write(f"SIM卡: SIM{sim_index + 1}\n")
        file.write(f"来电时间: {start_time.strftime('%H:%M:%S')}\n")
        file.write(f"结束时间: {end_time.strftime('%H:%M:%S')}\n")
        file.write(f"通话时长: {duration}\n")
        file.write("-" * 30 + "\n")  # 分隔线

def call_status_handler(driver, sim, call_info):
    """处理通话状态变化的回调函数"""
    global call_start_time, sim_index

    # 检测来电并接听
    if call_info["mRingingCallState"] == 5 and call_info["mCallState"] == 1:
        sim_index = 0 if sim == "SIM1" else 1
        print(f"{sim} 来电检测到，接听中...")
        driver.press_keycode(5)
        call_start_time = datetime.now()  # 记录接通时间

    # 检测挂断状态
    elif call_info["mCallState"] == 0 and call_start_time is not None:
        call_end_time = datetime.now()
        call_duration = (call_end_time - call_start_time).total_seconds()
        print(f"通话结束，通话时长: {call_duration} 秒")

        # 记录到日志
        log_call_to_txt("来电", sim_index, call_start_time, call_duration, call_end_time)

        # 重置通话状态
        call_start_time = None
        sim_index = None

def __main__(driver):
    """
    监听通话状态的主函数
    :param driver: 由主程序传入的 WebDriver 对象
    """
    print("开始执行 MT 的监听逻辑")
    global call_start_time, sim_index
    call_start_time = None
    sim_index = None

    # 注册回调函数并开始监控
    register_callback(lambda sim, call_info: call_status_handler(driver, sim, call_info))
    try:
        print("开始监听通话状态")
        monitor_call_state(driver)
        time.sleep(1)  # 避免频繁循环占用资源
    except Exception as e:
        print(f"监听任务失败: {e}")

