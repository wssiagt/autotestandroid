import time
from NetworkSwitch import NetworkSwitcher
from Zhujiao import prepare_for_dialing, run_call_test
from loadConfig import load_call_config
from NetworkValidation import NetworkValidator
from appium import webdriver
from appium.options.android import UiAutomator2Options

def main():
    # 初始化 Appium 驱动
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.device_name = "DUT"
    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)

    try:
        # 读取并更新 SIM 卡信息
        prepare_for_dialing(driver)

        # 加载配置文件
        config = load_call_config(file_path="call_config.txt")
        network_types = config.get("network_types", [])
        if not network_types:
            print("配置文件中未找到 network_types，终止程序。")
            return

        dial_number1 = config.get("dial_number1")
        dial_number2 = config.get("dial_number2")
        dial_times = config.get("dial_times", 1)
        wait_times = config.get("wait_time", 5)

        if not dial_number1 or not dial_number2:
            print("配置文件中未找到拨号号码，终止程序。")
            return

        network_switcher = NetworkSwitcher(driver)
        network_validator = NetworkValidator(driver)

        for network_type in network_types:
            # print(f"切换到网络类型: {network_type}")

            # 切换网络类型
            network_switcher.switch_network_type("SIM1", network_type)
            network_switcher.switch_network_type("SIM2", network_type)
            time.sleep(3)  # 等待网络切换完成

            # 验证网络注册
            sim1_valid = network_validator.ensure_network_registration("SIM1", network_type)
            sim2_valid = network_validator.ensure_network_registration("SIM2", network_type)

            if not sim1_valid or not sim2_valid:
                print(f"网络 {network_type} 验证失败，跳过后续操作。")
                continue

            # 拨号测试
            for _ in range(dial_times):
                # print("开始拨号测试...")
                run_call_test(driver, "SIM1", dial_number1)
                time.sleep(wait_times)  # 等待拨号完成

                run_call_test(driver, "SIM2", dial_number2)
                time.sleep(2)  # 等待拨号完成

        print("所有网络类型和拨号测试完成！")

    except Exception as e:
        print(f"程序运行中发生错误: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()