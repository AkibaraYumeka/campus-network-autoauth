from pathlib import Path

import tomlkit
from tomlkit import document, comment, nl
from loguru import logger

# TODO: check config

def _create_config(config_path: Path) -> None:
    """Create config file."""

    doc = document()

    doc.add(comment("认证门户的 IP 和端口号"))
    doc.add("portal_ip", "192.168.16.41")
    doc.add("portal_port", "801")
    doc.add(nl())

    doc.add(comment("学号和密码"))
    doc.add("username", "")
    doc.add("password", "")

    doc.add(nl())
    doc.add(comment("互联网服务提供商（如中国电信、中国移动、校园网）"))
    doc.add(comment("e.g. @telecom, @cmcc, @xyw"))
    doc.add(comment("需要根据实际可用 ISP 填写"))
    doc.add("isp", "")

    config_path.parent.mkdir(parents=True, exist_ok=True)

    with config_path.open("w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(doc))

    logger.info(f"Generated config file at \"{config_path}\"")

def _load_config(config_path: Path) -> tomlkit.TOMLDocument:
    """Load config file."""
    with config_path.open("r", encoding="utf-8") as f:
        logger.info(f"Loaded config file from \"{config_path}\"")
        return tomlkit.parse(f.read())
# TODO: add detection for config file

def setup_config(config_path: Path) -> tomlkit.TOMLDocument | None:
    """Setup the config system, detect config file automatically, generate and load it."""

    if config_path.exists():
        return _load_config(config_path)
    else:
        _create_config(config_path)
        return None
