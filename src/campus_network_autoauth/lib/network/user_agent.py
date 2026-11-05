import json
import os
import platform
import sys
from pathlib import Path

from fake_useragent import UserAgent
from loguru import logger

DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/135.0.0.0 Safari/537.36"
)


def _detect_device() -> tuple[str, str]:
    """Return device platforms and OS that fake_useragent supports."""

    if hasattr(sys, "getandroidapilevel") or "ANDROID_ROOT" in os.environ:
        return "mobile", "Android"

    system = platform.system()

    if system == "Windows":
        return "desktop", "Windows"
    if system == "Darwin":
        return ("mobile", "iOS") if sys.platform == "ios" else ("desktop", "Mac OS X")
    if system == "Linux":
        return "desktop", "Linux"

    logger.warning(
        f'[network.user_agent] Unknown platform: "{system}", falling back to Windows Desktop'
    )
    return "desktop", "Windows"


def _create_ua(ua_path: Path) -> dict:
    """Create User Agent profile."""

    try:
        device_type, device_os = _detect_device()
        ua_pool = UserAgent(
            browsers=["Chrome"],
            platforms=[device_type],
            os=[device_os],
            min_version=130,
        )

        ua_str = ua_pool.chrome
        if not isinstance(ua_str, str) or not ua_str:
            raise ValueError("fake_useragent returned an empty User-Agent")
        profile = {"user-agent": ua_str}
    except Exception as e:
        logger.warning(
            f"[network.user_agent] Failed to generate User-Agent, falling back to default: error={e}"
        )
        profile = {"user-agent": DEFAULT_UA}

    ua_path.parent.mkdir(parents=True, exist_ok=True)
    with ua_path.open("w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

    logger.info(f'[network.user_agent] Generated User-Agent profile at "{ua_path}"')
    return profile


def _load_ua(ua_path: Path) -> dict | None:
    """Load and validate User Agent profile; return None if missing or invalid."""

    if not ua_path.exists():
        logger.info(
            f'[network.user_agent] User-Agent profile at "{ua_path}" not found, will create one'
        )
        return None

    try:
        with ua_path.open("r", encoding="utf-8") as f:
            profile = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.error(
            f'[network.user_agent] Failed to parse User-Agent profile at "{ua_path}": error={e}'
        )
        return None

    ua_str = profile.get("user-agent") if isinstance(profile, dict) else None
    if not isinstance(ua_str, str) or not ua_str:
        logger.warning(
            f'[network.user_agent] User-Agent profile at "{ua_path}" is malformed (missing "user-agent")'
        )
        return None

    logger.debug(f'[network.user_agent] Loaded User-Agent profile from "{ua_path}"')

    return profile


def get_pinned_ua(ua_path: Path) -> str:
    """Get pinned User-Agent from profile or generate one."""

    profile = _load_ua(ua_path)
    if profile is None:
        profile = _create_ua(ua_path)

    ua_str = profile["user-agent"]
    logger.debug(f'[network.user_agent] Pinned User-Agent: "{ua_str}"')
    return ua_str
