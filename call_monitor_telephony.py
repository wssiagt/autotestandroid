# 获取电话状态信息，分别针对 SIM1 (Phone Id=0) 和 SIM2 (Phone Id=1)
def get_call_info():
    try:
        # 运行 adb shell dumpsys telephony.registry 命令
        result = subprocess.run(['adb', 'shell', 'dumpsys', 'telephony.registry'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

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

        current_phone_id = None  # 当前解析的是哪张 SIM 卡

        for line in result.stdout.splitlines():
            if "Phone Id=0" in line:
                current_phone_id = 0
            elif "Phone Id=1" in line:
                current_phone_id = 1

            # 处理 SIM 卡 1 的信息
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

            # 处理 SIM 卡 2 的信息
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

def monitor_call_state():
    # 初始化通话状态
    call_status_trigger1 = None
    call_status_trigger2 = None
    call_start_time = None
    call_stop_time = None
    while True:
        call_info_sim1, call_info_sim2 = get_call_info()
        # 判断 SIM 卡 1 的状态
        if call_info_sim1:
            # 被叫来电振铃中
            if call_status_trigger1 != "ACTIVATE" and call_info_sim1["mCallState"] == 1 and call_info_sim1["mRingingCallState"] == 5:
                print(f"SIM2来电(被叫)，来电号码: {call_info_sim1['mCallIncomingNumber']}")
            # 主叫振铃中
            elif call_status_trigger1 != "ACTIVATE" and call_info_sim1["mCallState"] == 2 and call_info_sim1["mForegroundCallState"] == 4:
                print("SIM2主叫振铃中")
            # 判断通话是否已接通（无论是主叫还是被叫）
            elif call_status_trigger1 != "ACTIVATE" and call_info_sim1["mCallState"] == 2 and call_info_sim1["mForegroundCallState"] == 1:
                print(f"SIM2通话已接通")
                call_status_trigger1 = "ACTIVATE"
                call_start_time = time.time()
                print("通话接通时间:", time.strftime('%H:%M:%S', time.localtime(call_start_time)))
            # 判断是否通话中
            elif call_info_sim1["mCallState"] == 2 and call_status_trigger1 == "ACTIVATE":
                print("SIM2通话中")
            # 判断通话结束
            elif call_info_sim1["mCallState"] == 0:
                if call_status_trigger1 == "ACTIVATE":
                    call_stop_time = time.time()
                    print("通话结束时间:", time.strftime('%H:%M:%S', time.localtime(call_stop_time)))
                    call_duration = call_stop_time - call_start_time
                    print("通话时长:", time.strftime('%H:%M:%S', time.gmtime(call_duration)))
                    call_status_trigger1 = "DEACTIVATE"   
                    
        # 判断 SIM 卡 2 (Phone Id=1) 的状态
        if call_info_sim2:
            # 被叫来电振铃中
            if call_status_trigger2 != "ACTIVATE" and call_info_sim2["mCallState"] == 1 and call_info_sim2["mRingingCallState"] == 5:
                print(f"SIM2来电(被叫)，来电号码: {call_info_sim2['mCallIncomingNumber']}")
            # 主叫振铃中
            elif call_status_trigger2 != "ACTIVATE" and call_info_sim2["mCallState"] == 2 and call_info_sim2["mForegroundCallState"] == 4:
                print("SIM2主叫振铃中")
            # 判断通话是否已接通（无论是主叫还是被叫）
            elif call_status_trigger2 != "ACTIVATE" and call_info_sim2["mCallState"] == 2 and call_info_sim2["mForegroundCallState"] == 1:
                print(f"SIM2通话已接通")
                call_status_trigger2 = "ACTIVATE"
                call_start_time = time.time() 
                print("通话接通时间:", time.strftime('%H:%M:%S', time.localtime(call_start_time)))
            # 判断是否通话中
            elif call_info_sim2["mCallState"] == 2 and call_status_trigger2 == "ACTIVATE":
                print("SIM2通话中")
            # 判断通话结束
            elif call_info_sim2["mCallState"] == 0:
                if call_status_trigger2 == "ACTIVATE":
                    call_stop_time = time.time() 
                    print("通话结束时间:", time.strftime('%H:%M:%S', time.localtime(call_stop_time)))
                    call_duration = call_stop_time - call_start_time
                    print("通话时长:", time.strftime('%H:%M:%S', time.gmtime(call_duration)))
                    call_status_trigger2 = "DEACTIVATE"
        time.sleep(2)

# 启动电话状态监听
if __name__ == "__main__":
    monitor_call_state()
