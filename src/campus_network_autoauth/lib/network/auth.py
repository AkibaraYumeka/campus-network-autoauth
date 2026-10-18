import socket

import requests

# TODO: add random UA

# check network status
def check_wired(test_url="http://www.apple.com/library/test/success.html"):
    try:
        response = requests.head(test_url, timeout=3, allow_redirects=False)
        if response.status_code in [ 200, 204]:
            # print("[DEBUG][check_wired] reponse.status_code ==", response.status_code)
            return True
        elif 300 <= response.status_code < 400:
            # print("[DEBUG][check_wired] reponse.status_code ==", response.status_code)
            return False
        else:
            # print("[DEBUG][check_wired] other exception status code ==", response.status_code)
            return False
    except requests.exceptions.RequestException as e:
        # print("[DEBUG][check_wired] disconnected, timeout or error:", e)
        return False

# grant terminal LAN IP
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

# log in to Dr.com
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
            print("[WARN] Authentication failed, please check your config file")
    except requests.RequestException as e:
        print(f"[ERROR] Get request failed: {e}")
