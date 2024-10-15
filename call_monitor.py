from appium.options.android import UiAutomator2Options
from appium import webdriver
import time
from time import sleep
from appium.webdriver.common.appiumby import AppiumBy
import subprocess
import os
from datetime import datetime

# 设置 Desired Capabilities
options = UiAutomator2Options()
options.platform_name = 'Android'
options.platform_version = '15'  # 根据设备的实际版本
options.device_name = 'PTP'  # 设备名称

# 监听通话状态
def monitor_call_state(activate_time):
    # 清理 logcat 缓存，确保读取的是最新的一行 logcat 信息
    subprocess.run(['adb', 'logcat', '-c'])  # 清除 logcat 缓存

    # 开启 logcat 读取
    process = subprocess.Popen(['adb', 'logcat', '-b', 'radio', '-d'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    latest_state = None  # 存储最新的状态
    active_detected = False  # 是否检测到 ACTIVE 状态
    
    # 只读取最新的几行 logcat 并处理
    while True:
        line = process.stdout.readline().decode('utf-8')
        if not line:
            break  # 如果没有更多的 logcat 输出，退出循环

        if activate_time not in line:
            print("logcat调试时间", activate_time)
            print(active_detected)
            # 检测 "processCallStateChange" 行
            if "processCallStateChange" in line:
                if "DIALING" in line:
                    latest_state = "DIALING"
                    #print(line)
                elif "ALERTING" in line:
                    latest_state = "ALERTING"
                    #print(line)
                elif "ACTIVE" in line:
                    latest_state = "ACTIVE"
                    active_detected = True
                    break  # 当通话建立时，退出循环，返回最新状态
                elif "DISCONNECTED" in line:
                    latest_state = "DISCONNECTED"
                    # print(line)
                    break  # 通话结束时退出循环，返回最新状态
                    
        # 如果已经检测到 ACTIVE 状态，则跳出循环，避免重复检测
        if active_detected:
            break
            
    return latest_state  # 只返回最新的状态