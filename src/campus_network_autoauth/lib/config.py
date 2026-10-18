from pathlib import Path

import tomlkit
from tomlkit import document, comment, nl
from loguru import logger

# TODO: check config

def create_config(config_path: Path) -> tomlkit.TOMLDocument:
    """Create config file."""

    doc = document()

    doc.add("auth_url", "http://192.168.16.41:801/eportal/portal/login")
    doc.add(nl())

    doc.add(comment("学号和密码"))
    doc.add("username", "")
    doc.add("password", "")

    doc.add(nl())
    doc.add(comment("运营商（中国电信、中国移动、校园网）"))
    doc.add(comment("可用选项：@telecom, @cmcc, xyw"))
    doc.add("isp", "")

    config_path.parent.mkdir(parents=True, exist_ok=True)

    with config_path.open("w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(doc))

    logger.info(f"Generated config file at \"{config_path}\". Run the script again after filling in your username, password, and ISP.")

    return doc

def load_config(config_path: Path) -> tomlkit.TOMLDocument:
    """Load config file."""
    with config_path.open("r", encoding="utf-8") as f:
        logger.info(f"Loaded config file at \"{config_path}\".")
        return tomlkit.parse(f.read())
