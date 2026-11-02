import json
import socket
import time

import requests
from loguru import logger

from campus_network_autoauth.lib.config import Config


def _has_lan_ip() -> bool:
    """Check whether the terminal has a LAN IP."""

    ip = _grant_lan_ip()
    return not ip.startswith(("127.", "169.254."))

def wait_for_lan_ip(timeout: float=120) -> bool:
    """Wait for a valid LAN IP address."""

    logger.debug(f"[network.auth] Waiting for a LAN IP, timeout={timeout}s")
    deadline = time.monotonic() + timeout
    retry_interval = 1
    while time.monotonic() < deadline:
        if _has_lan_ip():
            logger.info("[network.auth] LAN IP is ready")
            return True
        logger.debug(f"[network.auth] LAN IP or route not ready, retrying in {retry_interval}s")
        time.sleep(retry_interval)
    logger.error(f"[network.auth] Timeout waiting for LAN IP after {timeout}s")
    return False

def wait_for_portal(portal_ip: str, portal_port: int, timeout: float = 120) -> bool:
    """Wait for the portal to be reachable on the specified IP and port."""

    logger.debug(f"[network.auth] Waiting for portal {portal_ip}:{portal_port}, timeout={timeout}s")
    deadline = time.monotonic() + timeout
    retry_interval = 1
    while time.monotonic() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            if s.connect_ex((portal_ip, portal_port)) == 0:
                logger.info(f"[network.auth] Portal {portal_ip}:{portal_port} is reachable")
                return True
        logger.debug(f"[network.auth] Portal {portal_ip}:{portal_port} not reachable, retrying in {retry_interval}s")
        time.sleep(retry_interval)
    logger.error(f"[network.auth] Portal {portal_ip}:{portal_port} unreachable after {timeout}s")
    return False

def check_wired(test_url: str="http://connect.rom.miui.com/generate_204") -> bool:
    """Check whether the Wired is accessible."""

    try:
        with requests.head(test_url, timeout=3, allow_redirects=False) as response:
            if response.status_code == 204:
                logger.debug(f"[network.auth] Verified Wired session: status_code={response.status_code}")
                return True
            elif 300 <= response.status_code < 400 or response.status_code == 200:
                logger.debug(f"[network.auth] Detected captive portal interception: status_code={response.status_code}")
                return False
            else:
                logger.debug(f"[network.auth] Received unexpected response: test_url={test_url}, status_code={response.status_code}")
                return False
    except requests.exceptions.RequestException as e:
        logger.debug(f"[network.auth] Failed to reach Wired: error={e}")
        return False

def _grant_lan_ip() -> str:
    """Grant terminal LAN IP"""

    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(("10.255.255.255", 1))
        ip = st.getsockname()[0]
    except Exception as e:
        ip = "127.0.0.1"
        logger.debug(f"[network.auth] LAN IP route probe failed: error={e}")
    finally:
        st.close()
    return ip

# TODO: add auto grant MAC address function


def _parse_response(body: str) -> dict | None:
    """Parse Dr.COM response, accepting JSONP or plain JSON."""

    try:
        data = json.loads(body.strip())
    except json.JSONDecodeError:
        start, end = body.find("("), body.rfind(")")
        if start == -1 or end <= start:
            return None
        try:
            data = json.loads(body[start + 1 : end])
        except json.JSONDecodeError:
            return None
    return data if isinstance(data, dict) else None

def login(config: Config, ua: str) -> bool:
    """Log in to Dr.COM"""

    params = {
        "callback": "dr1003",
        "login_method": "1",
        "user_account": f",0,{config.account.username}{config.account.isp}",
        "user_password": config.account.password,
        "wlan_user_ip": _grant_lan_ip(),
        "wlan_user_ipv6": "",
        "wlan_user_mac": "",
        "wlan_ac_ip": "",
        "wlan_ac_name": "",
        "jsVersion": "4.1.3",
        "terminal_type": "1",
        "lang": "zh-cn"
    }

    raw_url = f"http://{config.portal.ip}"
    base_url = f"http://{config.portal.ip}:{config.portal.port}/eportal/portal/login"

    headers = {
        "User-Agent": ua,
        "Referer": raw_url
    }

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=5)

        data = _parse_response(response.text)
        if data is None:
            logger.warning(f"[network.auth] Authentication failed: unparsable response, body={response.text}")
            return False

        if data.get("result") == 1:
            logger.info("[network.auth] Logged in to the portal, successfully connected to the Wired")
            return True

        logger.warning(f"[network.auth] Authentication failed: data={data}")
        return False
    except requests.RequestException as e:
        logger.error(f"[network.auth] Login request failed: error={e}")
        return False
    except Exception as e:
        logger.opt(exception=e).error("[network.auth] Unexpected error during login")
        return False
