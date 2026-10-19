import sys

from loguru import logger

from campus_network_autoauth.lib.config import setup_config
from campus_network_autoauth.lib.logger import setup_logger
from campus_network_autoauth.lib.network import check_wired, login
from campus_network_autoauth.lib.path import CONFIG_PATH, LOG_DIR

# TODO: auto daemon

def main() -> None:
    setup_logger(LOG_DIR)

    if check_wired():
        logger.info("Wired, No need to re-login")
    else:
        logger.info("Disconnected from Wired or not authenticated, trying to log in")
        config = setup_config(CONFIG_PATH)
        if config == None:
            logger.warning("Config file not found Please fill in your username, password, and ISP, then try again.")
            sys.exit(0)
        login(config)

if __name__ == "__main__":
    main()
