import time
from appium import webdriver
from threading import Thread
from appium.options.android import UiAutomator2Options


def get_connected_devices():
    """获取通过 adb devices 连接的设备"""
    import subprocess
    result = subprocess.run(["adb", "devices"], stdout=subprocess.PIPE, text=True)
    lines = result.stdout.strip().split("\n")[1:]  # 跳过第一行 "List of devices attached"
    devices = [line.split("\t")[0] for line in lines if "device" in line]
    return devices


def control_device(device_config, script_module, server_url, drivers):
    """
    控制单个设备运行指定脚本模块
    :param device_config: 包含设备信息的字典
    :param script_module: 脚本模块路径或逻辑
    :param server_url: Appium 服务器 URL
    :param drivers: 用于存储 driver 对象的列表
    """
    # 创建 UiAutomator2Options 实例
    options = UiAutomator2Options()
    options.platform_name = device_config["platform_name"]
    options.device_name = device_config["device_name"]
    options.udid = device_config["udid"]

    # 启动 WebDriver
    driver = webdriver.Remote(server_url, options=options)
    drivers.append(driver)  # 将 driver 添加到共享的列表中
    try:
        print(f"{device_config['device_name']} 已连接，运行模块: {script_module.__name__}")

        # 调用模块逻辑，并传递 driver
        if hasattr(script_module, "run_call_tests"):
            script_module.run_call_tests(driver)  # 传递 drivers 列表
        elif hasattr(script_module, "__main__"):
            script_module.__main__(driver)
        else:
            print(f"模块 {script_module.__name__} 中未找到有效的入口函数")
    except Exception as e:
        print(f"设备 {device_config['device_name']} 执行任务失败: {e}")


if __name__ == "__main__":
    # 获取设备列表
    connected_devices = get_connected_devices()
    if len(connected_devices) < 2:
        print("需要至少两个设备连接才能运行此脚本")
        exit(1)

    # 配置设备 1 和设备 2 的信息
    device1_config = {
        "platform_name": "Android",
        "device_name": "Device1",
        "udid": connected_devices[0],
    }
    server_url_device1 = "http://127.0.0.1:4723"

    device2_config = {
        "platform_name": "Android",
        "device_name": "Device2",
        "udid": connected_devices[1],
    }
    server_url_device2 = "http://127.0.0.1:4725"

    # 动态导入模块
    import singlesim
    import MT

    # 用于存储 driver 对象的列表
    drivers = []

    # 创建线程分别运行两个设备的脚本
    thread1 = Thread(target=control_device, args=(device1_config, singlesim, server_url_device1, drivers))
    thread2 = Thread(target=control_device, args=(device2_config, MT, server_url_device2, drivers))

    thread1.start()
    thread2.start()

    thread1.join()
    for d in drivers:
        print("清理未关闭的会话...")
        d.quit()
    thread2.join()
    
    print("两个设备任务完成！")
