import socket

import requests
from loguru import logger

# TODO: add random UA

def check_wired(test_url: str="http://connect.rom.miui.com/generate_204") -> bool:
    """Check whether the Internet is accessible."""

    try:
        response = requests.head(test_url, timeout=3, allow_redirects=False, stream=True)
        if response.status_code == 204:
            logger.debug(f"Network check success. Status: {response.status_code}")
            return True
        elif 300 <= response.status_code < 400 or response.status_code == 200:
            logger.debug(f"Network intercepted by gateway. Status: {response.status_code}")
            return False
        else:
            logger.debug(f"Unexpeted status code from {test_url}: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.debug("Disconnected or timeout:", e)
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
    """Log in to Dr.COM"""

    params = {
        "callback": "dr1003",
        "login_method": "1",
        "user_account": ",0," + config["username"] + config["isp"],
        "user_password": config["password"],
        "wlan_user_ip": grant_lan_ip(),
        "wlan_user_ipv6": "",
        "wlan_user_mac": "",
        "wlan_ac_ip": "",
        "wlan_ac_name": "",
        "jsVersion": "4.1.3",
        "terminal_type": "1",
        "lang": "zh-cn"
    }

    raw_url = "http://" + config["portal_ip"]
    base_url = raw_url + ":" + config["portal_port"] + "/eportal/portal/login"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:157.0) Gecko/20100101 Firefox/157.0",
        "Referer": raw_url
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
