import json
import os
import platform
import sys
from pathlib import Path

from fake_useragent import UserAgent
from loguru import logger

def _detect_device():
    """Return device platforms and OS that fake_useragent supports."""

    device_type: str
    reason: str

    system_os = platform.system().lower()
    os_mapping = {
        "windows": "Windows",
        "darwin": "Mac OS X",
        "linux": "Linux",
        "anrdoid": "Anrdoid",
        "ios": "iOS",
        "ipados": "iPadOS"
    }

    device_os = os_mapping.get(system_os, "windows")

    # Android (include Termux)
    if hasattr(sys, "getandroidapilevel"):
        device_type, reason = "mobile", "Android (sys.getandroidapilevel)"
    elif any("ANDROID" in k.upper() for k in os.environ):
        device_type, reason = "mobile", "Android (environment variable)"

    else:
        system = platform.system()
        if system in ("iOS", "iPadOS"):
            device_type, reason = "mobile", f"{system}"
        elif system in ("Windows", "Darwin", "Linux"):
            device_type, reason = "desktop", f"{system}"
        else:
            device_type, reason = "desktop", f"unknown system ({system}), fallback"

    logger.debug(f"[network.user_agent] Detected device type: \"{device_type}\" ({reason})")
    logger.debug(f"[network.user_agent] Detected device OS: \"{device_os}\"")

    return device_type, device_os

def _create_ua(ua_path: Path) -> dict:
    """Create User Agent profile."""
    device_type, device_os = _detect_device()
    ua_pool = UserAgent(
        browsers=["Chrome"],
        platforms=[device_type],
        os=device_os,
        min_version=130
    )

    profile = {"user-agent": ua_pool.chrome}

    ua_path.parent.mkdir(parents=True, exist_ok=True)
    with ua_path.open("w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

    logger.info(f"[network.user_agent] Generated User-Agent profile at \"{ua_path}\"")
    return profile

def _load_ua(ua_path: Path) -> dict | None:
    """Load and validate User Agent profile; return None if missing or invalid."""

    if not ua_path.exists():
        logger.info(f"[network.user_agent] User-Agent profile at \"{ua_path}\" not found, will create one")
        return None

    try:
        with ua_path.open("r", encoding="utf-8") as f:
            profile = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.error(f"[network.user_agent] Failed to parse User-Agent profile at \"{ua_path}\": error={e}")
        return None

    ua_str = profile.get("user-agent") if isinstance(profile, dict) else None
    if not isinstance(ua_str, str) or not ua_str:
        logger.warning(f"[network.user_agent] User-Agent profile at \"{ua_path}\" is malformed (missing \"user-agent\")")
        return None

    logger.debug(f"[network.user_agent] Loaded User-Agent profile from \"{ua_path}\"")

    return profile

def get_pinned_ua(ua_path: Path) -> str:
    """Get pinned User-Agent from profile or generate one."""


    profile = _load_ua(ua_path)
    if profile is None:
        profile = _create_ua(ua_path)

    ua_str = profile["user-agent"]
    logger.debug(f"[network.user_agent] Pinned User-Agent: \"{ua_str}\"")
    return ua_str
