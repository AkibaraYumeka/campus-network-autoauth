# import argparse
import json
import os
import requests
import socket

# TODO: replace json config file to toml(but only works on python 3.11+)
# TODO: check config
# TODO: auto daemon

"""
an auto login script for Dr.COM campus network auth
"""

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.json")

# config
def create_config():
    # isp = ["@telecom", "@cmcc", "@"]
    default_config = "{\n\t\"auth_url\": \"http://192.168.16.41:801/eportal/portal/login\",\n\t\"username\": \"\",\n\t\"password\": \"\",\n\t\"isp\": \"\"\n}"
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(default_config)

def load_config():
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

# check network status
def check_wired(test_url="http://www.apple.com/library/test/success.html"):
    try:
        response = requests.get(test_url, timeout=3)
        if response.status_code == 200:
            return True
    except requests.RequestException:
        pass
    return False

def grant_lan_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP

# login
def login(config):
    params = {
        "callback": "dr1003",
        "login_method": "1",
        "user_account": ",0," + config["username"] + config["isp"],
        "user_password": config["password"],
        "wlan_user_ip": grant_lan_ip(),
        "wlan_user_ipv6": "",
        "wlan_user_mac": "000000000000",
        "wlan_ac_ip": "",
        "wlan_ac_name": "",
        "jsVersion": "4.1.3",
        "terminal_type": "1", # 1 = pc
        "lang": "zh-cn",
        "lang": "zh",
        "v": "3020"
    }

    base_url = config["auth_url"]

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:157.0) Gecko/20100101 Firefox/157.0",
        "Referer": "http://192.168.16.41/"
    }

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=5)
        response.encoding = "utf-8"

        print(f"[INFO] Authenticate server returned response: {response.text}")

        if "\"result\":1" in response.text:
            print("[INFO] Successfully connected to the Wired")
        else:
            print("[WARN] Authentication failed, please check your config")
    except requests.RequestException as e:
        print(f"[ERROR] Get request failed: {e}")

if __name__ == "__main__":
    # if check_wired():
    #     print("[INFO] Wired, No need to re-login.")
    # else:
        print("[INFO] Disconnected from Wired or not authenticated, trying to login...")
        if os.path.exists(config_path):
            config = load_config()
        else:
            create_config()
            print(f"[INFO] Generated config file at {config_path}, run the script again after wriring you account and password on it.")
            exit(0)
        login(config)

"""
request url
    http://192.168.16.41:801/eportal/portal/login?callback=dr1003&login_method=1&user_account=,0,9872134@telecom&user_password=quickbrownfox&wlan_user_ip=172.24.150.99&wlan_user_ipv6=&wlan_user_mac=000000000000&wlan_ac_ip=&wlan_ac_name=&jsVersion=4.1.3&terminal_type=1&lang=zh-cn&lang=zh&v=3020

return
    dr1003({"result":1,"msg":"Portal协议认证成功！"});
"""
