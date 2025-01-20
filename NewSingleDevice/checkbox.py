from appium.webdriver.common.appiumby import AppiumBy

def find_all_checkboxes(driver):
    """
    统计当前页面中 CheckBox 元素的数量。
    
    :param driver: Appium WebDriver 实例。
    """
    try:
        # 查找页面中的所有 CheckBox 元素
        checkboxes = driver.find_elements(AppiumBy.XPATH, "//android.widget.CheckBox")
        
        if not checkboxes:
            print("页面中未找到任何 CheckBox 元素。")
        else:
            print(f"在页面中找到 {len(checkboxes)} 个 CheckBox 元素。")

    except Exception as e:
        print(f"查找 CheckBox 元素时出错: {e}")


def find_parent_elements(driver):
    # 定位包含 'Use VoLTE' 的元素
    volte_elements = driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR,
                                          'new UiSelector().textContains("Use VoLTE")')

    # 定位包含 'Use 4G call' 的元素
    call_elements = driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR,
                                         'new UiSelector().textContains("Use 4G call")')

    # 合并两个列表
    elements = volte_elements + call_elements

    for element in elements:
        # 打印目标元素信息
        print("Target Element Text: ", element.text)
        print("Target Element Resource ID: ", element.get_attribute("resource-id"))

        # 初始化当前节点为目标元素
        current_element = element
        parent_found = False

        while not parent_found:
            try:
                # 尝试查找父级元素
                parent_candidates = driver.find_elements(AppiumBy.CLASS_NAME, "android.view.ViewGroup")
                for candidate in parent_candidates:
                    # 检查是否是当前节点的父级
                    child_elements = candidate.find_elements(AppiumBy.CLASS_NAME, current_element.get_attribute("class"))
                    if current_element in child_elements:
                        print("Parent Element Class Name: ", candidate.get_attribute("class"))
                        print("Parent Element Resource ID: ", candidate.get_attribute("resource-id"))
                        print("Parent Element Content Description: ", candidate.get_attribute("content-desc"))
                        print("Parent Element Text: ", candidate.text)
                        parent_found = True
                        break
                # 如果没找到父级元素，跳出循环避免死循环
                if not parent_found:
                    print("Parent not found for current element. Moving up the hierarchy.")
                    break
            except Exception as e:
                print(f"Error locating parent element for {element.text}: {e}")
                break