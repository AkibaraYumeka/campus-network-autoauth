import argparse
import sys
import time
from pathlib import Path

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

from .__version__ import __description__, __version__

# TODO: auto daemon

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__description__,
        add_help=False
    )
    parser.add_argument("-c", "--config", type=Path, help="Path to the config file")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the version number and exit"
    )
    return parser.parse_args()

def main() -> None:
    args = _parse_args()
    setup_logger(LOG_DIR, debug=args.debug)

    if check_wired():
        logger.info("[main] Wired session verified, re-login not required")
        sys.exit(0)

    logger.info("[main] Disconnected from Wired or not authenticated, trying to log in")

    target_config_path = args.config or CONFIG_PATH

    if args.config:
        logger.debug(f"[main] Using custom config path: {target_config_path}")

    result = setup_config(target_config_path)

    match result:
        case Ok(config=config):
            pass
        case Created():
            logger.info("[main] Config file template created, please fill it in and run again")
            sys.exit(0)
        case Invalid():
            logger.error("[main] Config is invalid, please fix it and run again")
            sys.exit(1)

    if not wait_for_lan_ip(str(config.portal.ip), timeout=120):
        logger.error("[main] Could not determine a route to the portal, please check your network connection")
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
