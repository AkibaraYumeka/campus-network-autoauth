import sys

from loguru import logger

from campus_network_autoauth.lib.config import setup_config
from campus_network_autoauth.lib.logger import setup_logger
from campus_network_autoauth.lib.network import check_wired, login, get_pinned_ua
from campus_network_autoauth.lib.path import CONFIG_PATH, LOG_DIR, UA_PATH

# TODO: auto daemon

def main() -> None:
    setup_logger(LOG_DIR, debug=False)

    if check_wired():
        logger.info("[main] Wired session verified, re-login not required")
    else:
        logger.info("[main] Disconnected from Wired or not authenticated, trying to log in")
        config = setup_config(CONFIG_PATH)
        if config is None:
            sys.exit(0)
        if config is False:
            sys.exit(1)
        if not login(config, get_pinned_ua(UA_PATH)):
            sys.exit(1)

if __name__ == "__main__":
    main()
