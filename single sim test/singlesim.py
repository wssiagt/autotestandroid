from appium.webdriver.common.appiumby import AppiumBy
from MO import (
    dial_number_with_sim,
    monitor_and_hang_up_call
)
import time
from datetime import datetime

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

def run_call_tests(driver):
    """
    执行拨号测试，使用外部传入的 driver
    """
    # 加载拨号配置
    call_config = load_call_config()
    dial_number = call_config["dial_number"]
    dial_times = call_config["dial_times"]
    dial_duration = call_config["dial_duration"]
    wait_time = call_config["wait_time"]

    # sim_info = get_sim_info(driver)
    for i in range(dial_times):
        print(f"开始第 {i + 1} 轮通话...")
        start_time = datetime.now()
        dial_number_with_sim(driver, dial_number, sim_name="SIM1")
        monitor_and_hang_up_call(driver,
            sim_index=0,
            sim_name="SIM1",
            duration=dial_duration,
            dial_number=dial_number
        )
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        # log_call_to_txt("拨号", "SIM1", start_time, duration, end_time)
        time.sleep(wait_time)
        print(f"第 {i + 1} 轮通话结束\n"
              f"-----------------------------------")
    print("所有通话测试完成")
    #for d in driver_container:
        #print("关闭appium会话")
        #d.quit()
