import socket

import requests
from loguru import logger

# TODO: add random UA

def check_wired(test_url: str="http://www.apple.com/library/test/success.html") -> bool:
    """Check whether the Internet is accessible."""

    try:
        response = requests.head(test_url, timeout=3, allow_redirects=False)
        if response.status_code in [ 200, 204]:
            logger.debug(f"reponse.status_code == {response.status_code}")
            return True
        elif 300 <= response.status_code < 400:
            logger.debug(f"reponse.status_code == {response.status_code}")
            return False
        else:
            logger.debug(f"Other exception status code == {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.debug("Disconnected, timeout or error:", e)
        return False

def grant_lan_ip() -> str:
    """Grant terminal LAN IP"""

    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP

def login(config: dict) -> bool:
    """Log in to Dr.com"""

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

        logger.debug(f"Authenticate server returned response: {response.text}")

        if "\"result\":1" in response.text:
            logger.info("Successfully connected to the Wired")
        else:
            logger.warning("Authentication failed, please check your config file")
    except requests.RequestException as e:
        logger.error(f"Get request failed: {e}")
