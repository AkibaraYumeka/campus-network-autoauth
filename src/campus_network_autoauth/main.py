import sys

from loguru import logger

from campus_network_autoauth.lib.config import create_config, load_config
from campus_network_autoauth.lib.logger import setup_logger
from campus_network_autoauth.lib.network import check_wired, login
from campus_network_autoauth.lib.path import CONFIG_PATH, LOG_DIR

# TODO: auto daemon

def main() -> None:
    setup_logger(LOG_DIR, debug=True)

    if check_wired():
        logger.info("Wired, No need to re-login.")
    else:
        logger.info("Disconnected from Wired or not authenticated, trying to log in...")
        if CONFIG_PATH.exists():
            config = load_config(CONFIG_PATH)
        else:
            create_config(CONFIG_PATH)
            sys.exit(0)
        login(config)

if __name__ == "__main__":
    main()
