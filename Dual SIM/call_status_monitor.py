import time
from time import sleep

last_call_info_sim1 = None
last_call_info_sim2 = None
callback = None

def get_call_info(driver):
    try:
        # result = subprocess.run(['adb', 'shell', 'dumpsys', 'telephony.registry'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # 使用 Appium 执行 shell 命令替代 subprocess
        result = driver.execute_script("mobile: shell", {
            "command": "dumpsys",
            "args": ["telephony.registry"],
            "includeStderr": True,  # 包含错误输出
            "timeout": 5000         # 设置超时时间（毫秒）
        })
        
        output = result.get("stdout")  # 提取 stdout 内容
        # print(output.splitlines())
        call_info_sim1 = {
            "PhoneId": 0,
            "mCallState": None,
            "mRingingCallState": None,
            "mForegroundCallState": None,
            "mBackgroundCallState": None,
            "mCallIncomingNumber": None
        }
        call_info_sim2 = {
            "PhoneId": 1,
            "mCallState": None,
            "mRingingCallState": None,
            "mForegroundCallState": None,
            "mBackgroundCallState": None,
            "mCallIncomingNumber": None
        }
        current_phone_id = None
        for line in output.splitlines():
            if "Phone Id=0" in line:
                current_phone_id = 0
            elif "Phone Id=1" in line:
                current_phone_id = 1
            if current_phone_id == 0:
                if "mCallState" in line:
                    call_info_sim1["mCallState"] = int(line.split('=')[-1].strip())
                elif "mRingingCallState" in line:
                    call_info_sim1["mRingingCallState"] = int(line.split('=')[-1].strip())
                elif "mForegroundCallState" in line:
                    call_info_sim1["mForegroundCallState"] = int(line.split('=')[-1].strip())
                elif "mBackgroundCallState" in line:
                    call_info_sim1["mBackgroundCallState"] = int(line.split('=')[-1].strip())
                elif "mCallIncomingNumber" in line:
                    call_info_sim1["mCallIncomingNumber"] = line.split('=')[-1].strip()
            elif current_phone_id == 1:
                if "mCallState" in line:
                    call_info_sim2["mCallState"] = int(line.split('=')[-1].strip())
                elif "mRingingCallState" in line:
                    call_info_sim2["mRingingCallState"] = int(line.split('=')[-1].strip())
                elif "mForegroundCallState" in line:
                    call_info_sim2["mForegroundCallState"] = int(line.split('=')[-1].strip())
                elif "mBackgroundCallState" in line:
                    call_info_sim2["mBackgroundCallState"] = int(line.split('=')[-1].strip())
                elif "mCallIncomingNumber" in line:
                    call_info_sim2["mCallIncomingNumber"] = line.split('=')[-1].strip()
        return call_info_sim1, call_info_sim2
    except Exception as e:
        print(f"获取电话状态信息失败: {e}")
    return None, None
    
def register_callback(cb):
    global callback
    callback = cb

def call_infor_update(call_info_sim1, call_info_sim2):
    global last_call_info_sim1, last_call_info_sim2
    if call_info_sim1 != last_call_info_sim1:
        last_call_info_sim1 = call_info_sim1
        if callback:
            callback("SIM1", call_info_sim1)
    if call_info_sim2 != last_call_info_sim2:
        last_call_info_sim2 = call_info_sim2
        if callback:
            callback("SIM2", call_info_sim2)

def monitor_call_state(driver):
    call_status_trigger1 = None
    call_status_trigger2 = None
    call_start_time = None
    call_stop_time = None
    while True:
        call_info_sim1, call_info_sim2 = get_call_info(driver)
        call_infor_update(call_info_sim1, call_info_sim2)
        if call_info_sim1:
            if call_status_trigger1 != "ACTIVATE" and call_info_sim1["mCallState"] == 1 and call_info_sim1["mRingingCallState"] == 5:
                print(f"SIM1来电(被叫)，来电号码: {call_info_sim1['mCallIncomingNumber']}")
            elif call_status_trigger1 != "ACTIVATE" and call_info_sim1["mCallState"] == 2 and call_info_sim1["mForegroundCallState"] == 4:
                print("SIM1主叫振铃中")
            elif call_status_trigger1 != "ACTIVATE" and call_info_sim1["mCallState"] == 2 and call_info_sim1["mForegroundCallState"] == 1:
                print(f"SIM1通话已接通")
                call_status_trigger1 = "ACTIVATE"
                call_start_time = time.time()
                print("通话接通时间:", time.strftime('%H:%M:%S', time.localtime(call_start_time)))
            elif call_info_sim1["mCallState"] == 2 and call_status_trigger1 == "ACTIVATE":
                print("SIM1通话中")
            elif call_info_sim1["mCallState"] == 0:
                if call_status_trigger1 == "ACTIVATE":
                    call_stop_time = time.time()
                    print("SIM1通话已结束")
                    print("通话结束时间:", time.strftime('%H:%M:%S', time.localtime(call_stop_time)))
                    call_duration = call_stop_time - call_start_time
                    print("通话时长:", time.strftime('%H:%M:%S', time.gmtime(call_duration)))
                    call_status_trigger1 = "DEACTIVATE"   
        if call_info_sim2:
            if call_status_trigger2 != "ACTIVATE" and call_info_sim2["mCallState"] == 1 and call_info_sim2["mRingingCallState"] == 5:
                print(f"SIM2来电(被叫)，来电号码: {call_info_sim2['mCallIncomingNumber']}")
            elif call_status_trigger2 != "ACTIVATE" and call_info_sim2["mCallState"] == 2 and call_info_sim2["mForegroundCallState"] == 4:
                print("SIM2主叫振铃中")
            elif call_status_trigger2 != "ACTIVATE" and call_info_sim2["mCallState"] == 2 and call_info_sim2["mForegroundCallState"] == 1:
                print(f"SIM2通话已接通")
                call_status_trigger2 = "ACTIVATE"
                call_start_time = time.time()
                print("通话接通时间:", time.strftime('%H:%M:%S', time.localtime(call_start_time)))
            elif call_info_sim2["mCallState"] == 2 and call_status_trigger2 == "ACTIVATE":
                print("SIM2通话中")
            elif call_info_sim2["mCallState"] == 0:
                if call_status_trigger2 == "ACTIVATE":
                    call_stop_time = time.time()
                    print("SIM2通话已结束")
                    print("通话结束时间:", time.strftime('%H:%M:%S', time.localtime(call_stop_time)))
                    call_duration = call_stop_time - call_start_time
                    print("通话时长:", time.strftime('%H:%M:%S', time.gmtime(call_duration)))
                    call_status_trigger2 = "DEACTIVATE"
        time.sleep(1)

if __name__ == "__main__":
    monitor_call_state()