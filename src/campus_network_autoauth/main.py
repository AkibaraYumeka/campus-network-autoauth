from pathlib import Path

from campus_network_autoauth.lib.config import create_config, load_config
from campus_network_autoauth.lib.network import check_wired, login

# TODO: auto daemon

config_path = Path(__file__).resolve().parent/"config.toml"

def main() -> None:
    if check_wired():
        print("[INFO] Wired, No need to re-login.")
    else:
        print("[INFO] Disconnected from Wired or not authenticated, trying to log in...")
        if config_path.exists():
            config = load_config(config_path)
        else:
            create_config(config_path)
            print(f"[INFO] Generated config file at {config_path}. Run the script again after filling in your username, password, and ISP.")
            exit(0)
        login(config)

if __name__ == "__main__":
    main()
