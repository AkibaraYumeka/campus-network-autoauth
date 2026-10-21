import sys

from loguru import logger

from campus_network_autoauth.lib.config import setup_config, Created, Invalid, Ok
from campus_network_autoauth.lib.logger import setup_logger
from campus_network_autoauth.lib.network import check_wired, login, get_pinned_ua
from campus_network_autoauth.lib.path import CONFIG_PATH, LOG_DIR, UA_PATH

# TODO: auto daemon

def main() -> None:
    # TODO: add args like `--config={path} | -c`, `--debug | --no-debug`, `--help`, `--version | -V`...
    setup_logger(LOG_DIR, debug=False)

    if check_wired():
        logger.info("[main] Wired session verified, re-login not required")
        sys.exit(0)

    logger.info("[main] Disconnected from Wired or not authenticated, trying to log in")
    result = setup_config(CONFIG_PATH)
    match result:
        case Ok(config=config):
            if not login(config, get_pinned_ua(UA_PATH)):
                sys.exit(1)
        case Created():
            logger.info("[main] Config file template created, please fill it in and run again")
            sys.exit(0)
        case Invalid():
            logger.error("[main] Config is invalid, please fix it and run again")
            sys.exit(1)

if __name__ == "__main__":
    main()
