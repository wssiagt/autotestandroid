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
options.device_name = 'XXX'  # 设备名称

# 假设要拨打的电话号码
phone_number = "XXXXXXXXX"

# 指定通话次数
total_call_count = 5  # 你可以根据需要修改通话次数

# 指定日志文件的保存路径
log_dir = "XXXXXXXXXXXXXXXXXX"
log_file_path = os.path.join(log_dir, "call_log.txt")

# 如果日志目录不存在，则创建
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 记录通话日志
call_log = []

# 连接到 Appium 服务器
driver = webdriver.Remote('http://127.0.0.1:XXXX', options=options)
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
# 拨打电话的功能
def make_call():
    # 找到包含 'phone' 的元素并点击打开拨号界面
    elements = driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("phone")')
    if elements:
        for element in elements:
            print(f"找到元素，准备点击：{element.get_attribute('content-desc')}")
            element.click()
            sleep(1)  # 每次点击后等待几秒
    else:
        print("未找到包含 'phone' 的元素")

    # 遍历电话号码中的每个数字，并逐个点击
    for digit in phone_number:
        element = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                                      f'new UiSelector().resourceIdMatches(".*dialpad.*num.*").text("{digit}")')
        element.click()
        sleep(0.3)  # 每次点击后稍作等待

    # 拨出电话
    element = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceIdMatches(".*dialButton.*")')

    if element:
        print('拨号键找到，即将拨打电话')
        element.click()
        sleep(0.5)
    else:
        print('No dial button found')
# 多次通话循环
for call_count in range(total_call_count):
    print(f"第 {call_count + 1} 次通话开始")

    # 重置通话状态为初始值
    call_state = None

    # 获取当前时间作为通话开始时间，用于过滤 logcat 日志
    activate_time = datetime.now().strftime("%H:%M:%S")

    # 拨打电话
    make_call()
    
    # 监控通话状态直到通话建立或结束
    while True:
        time.sleep(1)
        call_state = monitor_call_state(activate_time)
        print("通话状态：",call_state)

        if call_state == "ACTIVE":
            print("通话已建立，等待10秒后挂断...")
            start_time = time.time()
            time.sleep(11)
            duration = time.time() - start_time

            # 挂断电话
            driver.press_keycode(6)
            print(f"通话已挂断，通话时长：{duration:.2f}秒")

            # 记录通话日志
            call_log.append({
                'time': time.strftime("%Y-%m-%d %H:%M:%S"),
                'state': "Completed",
                'duration': duration
            })
            break  # 通话结束后退出当前循环
        elif call_state == "DIALING":
            print("正在拨号，等待通话建立...")
        elif call_state == "ALERTING":
            print("电话响铃中，等待接听...")
        elif call_state == "DISCONNECTED":
            print("通话未接通或已结束")
            break  # 通话结束后退出当前循环

    # 等待一段时间后发起下一次通话
    print("等待 5 秒后开始下一次通话...")
    call_state = None
    sleep(5)

# 将通话日志写入文件
with open(log_file_path, 'a') as f:
    for entry in call_log:
        f.write(f"{entry['time']}, 状态: {entry['state']}, 通话时长: {entry['duration']}秒\n")

# 关闭会话
driver.quit()
