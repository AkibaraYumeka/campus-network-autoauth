import sys
from pathlib import Path

from campus_network_autoauth.lib.path import CONFIG_PATH
from campus_network_autoauth.lib.config import create_config, load_config
from campus_network_autoauth.lib.network import check_wired, login

# TODO: auto daemon

def main() -> None:
    if check_wired():
        print("[INFO] Wired, No need to re-login.")
    else:
        print("[INFO] Disconnected from Wired or not authenticated, trying to log in...")
        if CONFIG_PATH.exists():
            config = load_config(CONFIG_PATH)
        else:
            create_config(CONFIG_PATH)
            print(f"[INFO] Generated config file at {CONFIG_PATH}. Run the script again after filling in your username, password, and ISP.")
            exit(0)
        login(config)

if __name__ == "__main__":
    main()
