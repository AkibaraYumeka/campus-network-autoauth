from pathlib import Path
from tomlkit import document, comment, nl
import tomlkit
import requests
import socket

# TODO: check config
# TODO: auto daemon

config_path = Path(__file__).resolve().parent/"config.toml"

def create_config(path: Path) -> tomlkit.TOMLDocument:
    doc = document()

    doc.add("auth_url", "http://192.168.16.41:801/eportal/portal/login")
    doc.add(nl())

    doc.add(comment("学号和密码"))
    doc.add("username", "")
    doc.add("password", "")

    doc.add(nl())
    doc.add(comment("运营商（中国电信、中国移动、校园网）"))
    doc.add(comment("可用选项：@telecom, @cmcc, xyw"))
    doc.add("isp", "")

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(doc))

    return doc

def load_config(path: Path) -> tomlkit.TOMLDocument:
    with open(config_path, "r", encoding="utf-8") as f:
        return tomlkit.parse(f.read())

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
        "lang": ["zh-cn","zh"],
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

if __name__ == "__main__":
    if check_wired():
        print("[INFO] Wired, No need to re-login.")
    else:
        print("[INFO] Disconnected from Wired or not authenticated, trying to log in...")
        if config_path.exists():
            config = load_config(config_path)
        else:
            create_config(config_path)
            print(f"[INFO] Generated config file at {config_path}, run the script again after writing you username and password on it.")
            exit(0)
        login(config)
