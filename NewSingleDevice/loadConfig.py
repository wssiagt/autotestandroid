import os
import time
from appium.webdriver.common.appiumby import AppiumBy
from basicOperation import BaseOperations  # 使用基础操作模块

def load_call_config(driver=None, file_path="call_config.txt"):
    """加载通话配置并动态更新 SIM 卡信息"""
    config = {}
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, value = line.split("=", 1)
                        value = parse_config_value(value)
                        config[key.strip()] = value
                    else:
                        print(f"跳过无效行: {line}")
        else:
            print(f"配置文件 {file_path} 不存在，将创建新文件。")

        if driver:
            sim_info = get_sim_info(driver)
            
            config.update(sim_info)
            save_call_config(file_path, config)

        # 验证必需的键值是否存在
        required_keys = ["SIM_1_OPERATOR", "SIM_1_NUMBER", "SIM_2_OPERATOR", "SIM_2_NUMBER"]
        for key in required_keys:
            if key not in config or not config[key]:
                print(f"警告：配置文件中缺少必要键值 {key}")

    except Exception as e:
        print(f"加载配置文件时发生错误: {e}")
    return config



def parse_config_value(value):
    """解析配置值"""
    if value.isdigit():
        return int(value)
    elif value.lower() in ("true", "false"):
        return value.lower() == "true"
    elif "," in value:
        return [v.strip() for v in value.split(",")]
    return value.strip()

def get_sim_info(driver):
    """获取设备中 SIM 卡和运营商信息"""
    base_ops = BaseOperations(driver)  # 基于基础操作模块
    base_ops.wake_up_screen()
    base_ops.go_home()
    time.sleep(0.2)
    base_ops.enter_data_setting()
    time.sleep(0.5)
    sim_info = {}
    for sim_id in ["sim_1", "sim_2"]:
        try:
            sim_element = driver.find_element(AppiumBy.ID, f"com.android.phone:id/{sim_id}")
            operator_name = sim_element.find_element(AppiumBy.ID, "com.android.phone:id/title").text
            sim_number = sim_element.find_element(AppiumBy.ID, "com.android.phone:id/summary").text
            sim_info[f"{sim_id.upper()}_OPERATOR"] = operator_name
            sim_info[f"{sim_id.upper()}_NUMBER"] = sim_number
        except Exception as e:
            print(f"Error accessing {sim_id.upper()}: {e}")
    return sim_info

def save_call_config(file_path, config):
    """将更新后的配置保存到文件"""
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            for key, value in config.items():
                if isinstance(value, list):
                    value = ",".join(value)
                file.write(f"{key}={value}\n")
    except Exception as e:
        print(f"保存配置文件时发生错误: {e}")
