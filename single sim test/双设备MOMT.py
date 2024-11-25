import time
from appium import webdriver
from threading import Thread
from appium.options.android import UiAutomator2Options
import subprocess
import os


def load_config(file_path="config.txt"):
    """加载设备配置文件"""
    config = {}
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()
    return config


def get_connected_devices():
    """获取通过 adb devices 连接的设备"""
    result = subprocess.run(["adb", "devices"], stdout=subprocess.PIPE, text=True)
    lines = result.stdout.strip().split("\n")[1:]  # 跳过第一行 "List of devices attached"
    devices = [line.split("\t")[0] for line in lines if "device" in line]
    return devices


def control_device(device_config, script_path, server_url):
    """控制单个设备运行指定脚本"""
    # 创建 UiAutomator2Options 实例
    options = UiAutomator2Options()
    options.platform_name = device_config["platform_name"]
    options.device_name = device_config["device_name"]
    options.udid = device_config["udid"]

    driver = webdriver.Remote(server_url, options=options)
    try:
        print(f"{device_config['device_name']} 已连接，运行脚本: {script_path}")
        exec(open(script_path).read(), {"driver": driver})  # 运行对应的脚本
    except Exception as e:
        print(f"设备 {device_config['device_name']} 执行任务失败: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    # 加载配置
    config = load_config("config.txt")
    
    # 获取设备列表
    connected_devices = get_connected_devices()
    if len(connected_devices) < 2:
        print("需要至少两个设备连接才能运行此脚本")
        exit(1)

    # 设置设备 1 和设备 2 的配置
    device1_config = {
        "platform_name": config.get("platform_name", "Android"),
        "device_name": config.get("device1_name", "Device1"),
        "udid": connected_devices[0],
    }
    server_url_device1 = config.get("server_url_device1", "http://127.0.0.1:4723")

    device2_config = {
        "platform_name": config.get("platform_name", "Android"),
        "device_name": config.get("device2_name", "Device2"),
        "udid": connected_devices[1],
    }
    server_url_device2 = config.get("server_url_device2", "http://127.0.0.1:4725")

    # momi.py 和 MT.py 路径
    momi_script = "momi.py"
    mt_script = "MT.py"

    # 创建线程分别控制两个设备
    thread1 = Thread(target=control_device, args=(device1_config, momi_script, server_url_device1))
    thread2 = Thread(target=control_device, args=(device2_config, mt_script, server_url_device2))

    # 启动线程
    thread1.start()
    thread2.start()

    # 等待线程完成
    thread1.join()
    thread2.join()

    print("两个设备任务完成！")
