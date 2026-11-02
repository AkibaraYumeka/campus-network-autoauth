import sys
import time

from loguru import logger

from campus_network_autoauth.lib.config import Created, Invalid, Ok, setup_config
from campus_network_autoauth.lib.logger import setup_logger
from campus_network_autoauth.lib.network import (
    check_wired,
    get_pinned_ua,
    login,
    wait_for_lan_ip,
    wait_for_portal,
)
from campus_network_autoauth.lib.path import CONFIG_PATH, LOG_DIR, UA_PATH

# TODO: auto daemon

def main() -> None:
    # TODO: add args like `--config={path} | -c`, `--debug | --no-debug`, `--help`, `--version | -V`...
    setup_logger(LOG_DIR, debug=True)

    if not wait_for_lan_ip(timeout=120):
        logger.error("[main] Could not determine a LAN IP or route, please check your network connection")
        sys.exit(1)

    if check_wired():
        logger.info("[main] Wired session verified, re-login not required")
        sys.exit(0)

    logger.info("[main] Disconnected from Wired or not authenticated, trying to log in")
    result = setup_config(CONFIG_PATH)
    match result:
        case Ok(config=config):
            pass
        case Created():
            logger.info("[main] Config file template created, please fill it in and run again")
            sys.exit(0)
        case Invalid():
            logger.error("[main] Config is invalid, please fix it and run again")
            sys.exit(1)

    if not wait_for_portal(str(config.portal.ip), config.portal.port, timeout=120):
        logger.error("[main] Portal unreachable, please check your network connection")
        sys.exit(1)

    ua = get_pinned_ua(UA_PATH)
    for attempt in range(1, config.etc.max_login_attempts + 1):
        logger.info(f"[main] Login attempt {attempt}/{config.etc.max_login_attempts} to log in")
        if login(config, ua):
            sys.exit(0)
        if attempt < config.etc.max_login_attempts:
            time.sleep(min(2 ** attempt, 10))
    logger.error(f"[main] Failed to log in after {config.etc.max_login_attempts} attempts, please check your credentials and network connection")
    sys.exit(1)

if __name__ == "__main__":
    main()
