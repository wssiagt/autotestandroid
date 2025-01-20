# Module: network_validation.py
import re
import time

NETWORK_TYPE_MAPPING = {
    "5G": ["5G NSA", "5G SA"],
    "4G": ["4G", "LTE"],
    "3G": ["3G"],
    "2G": ["2G"]
}

class NetworkValidator:
    def __init__(self, driver):
        self.driver = driver

    def validate_network_registration(self, sim_slot, target_networks):
        try:
            result = self.driver.execute_script("mobile: shell", {
                "command": "dumpsys",
                "args": ["telephony.registry"],
                "includeStderr": True,
                "timeout": 5000
            })

            if "stdout" not in result:
                print("Error: Failed to fetch telephony registry information.")
                return False

            output = result["stdout"]
            phone_id = 0 if sim_slot.upper() == "SIM1" else 1
            sim_identifier = f"Phone Id={phone_id}"

            if sim_identifier not in output:
                print(f"Error: SIM slot {sim_slot} (Phone Id={phone_id}) not found in telephony registry output.")
                return False

            sim_info_start = output.find(sim_identifier)
            if sim_info_start == -1:
                print(f"Error: SIM slot {sim_slot} (Phone Id={phone_id}) not found in telephony registry output.")
                return False

            next_sim_start = output.find("Phone Id=", sim_info_start + len(sim_identifier))
            sim_info_final = output.find("local logs")
            sim_info_end = min(filter(lambda x: x != -1, [next_sim_start, sim_info_final]))
            sim_info = output[sim_info_start:sim_info_end]

            # Extract fields
            voice_radio_tech, data_radio_tech, display_network, override_network, data_connection_state = None, None, None, None, None
            for line in sim_info.splitlines():
                if "getRilVoiceRadioTechnology" in line:
                    match = re.search(r"getRilVoiceRadioTechnology=(\d+)", line)
                    if match:
                        voice_radio_tech = match.group(1).strip()
                if "getRilDataRadioTechnology" in line:
                    match = re.search(r"getRilDataRadioTechnology=(\d+)", line)
                    if match:
                        data_radio_tech = match.group(1).strip()
                if "mTelephonyDisplayInfo" in line:
                    if "network=" in line:
                        display_network = line.split("network=")[-1].split(",")[0].strip()
                    if "overrideNetwork=" in line:
                        override_network = line.split("overrideNetwork=")[-1].split(",")[0].strip()
                if "mDataConnectionState" in line:
                    match = re.search(r"mDataConnectionState=(\d+)", line)
                    if match:
                        data_connection_state = int(match.group(1))

            # Validate against target networks
            for target_network in target_networks:
                if target_network.lower() == "5g sa" and voice_radio_tech == "20" or data_radio_tech == "20":
                    print(f"Validation successful: SIM{phone_id + 1} is registered on 5G SA network.")
                    return True
                elif target_network.lower() == "5g nsa" and voice_radio_tech == "14" and override_network == "NR_NSA":
                    print(f"Validation successful: SIM{phone_id + 1} is registered on 5G NSA network.")
                    return True
                elif target_network.lower() == "4g" and voice_radio_tech == "14" and display_network in ["LTE", "LTE_CA"]:
                    print(f"Validation successful: SIM{phone_id + 1} is registered on 4G network.")
                    return True
                elif target_network.lower() == "3g" and voice_radio_tech == "3":
                    print(f"Validation successful: SIM{phone_id + 1} is registered on 3G network.")
                    return True
                elif target_network.lower() == "2g" and voice_radio_tech == "16": # and data_radio_tech == "2"
                    print(f"Validation successful: SIM{phone_id + 1} is registered on 2G network.")
                    return True

            print(f"{sim_slot} is not registered on {target_networks}.")
            return False
        except Exception as e:
            print(f"Error validating network registration: {e}")
            return False

    #def ensure_network_registration(self, sim_slot, target_network, retries=10, interval=3):
        #target_networks = NETWORK_TYPE_MAPPING.get(target_network.upper(), [target_network])
        #for attempt in range(retries):
            #if self.validate_network_registration(sim_slot, target_networks):
                #return True
            #time.sleep(interval)
        #print(f"{sim_slot} failed to register to target network {target_networks}.")
        #return False

    def ensure_network_registration(self, sim_slot, target_network, retries=8, interval=4):
        target_network_short = target_network[:2]  # 对传入的 target_network 做切片预处理
        target_networks = NETWORK_TYPE_MAPPING.get(target_network_short.upper(), [target_network_short])
        for attempt in range(retries):
            if self.validate_network_registration(sim_slot, target_networks):
                return True
            time.sleep(interval)
        print(f"{sim_slot} failed to register to target network {target_networks}.")
        return False