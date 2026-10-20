from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Literal

import tomlkit
from loguru import logger
from pydantic import BaseModel, ValidationError, Field
from tomlkit import document, table, comment, nl

IPV4_PATTERN = (
    r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
    r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)

class PortalConfig(BaseModel):
    ip: str = Field(
        min_length=1, str_strip_whitespace=True, pattern=IPV4_PATTERN
    )
    port: int = Field(ge=1, le=65535)

class AccountConfig(BaseModel):
    username: str = Field(min_length=1, str_strip_whitespace=True)
    password: str = Field(min_length=1)
    isp: str = Field(
        min_length=1, str_strip_whitespace=True, pattern=r"^@[a-zA-Z0-9]+$"
    )

class Config(BaseModel):
    portal: PortalConfig
    account: AccountConfig

@dataclass(frozen=True, slots=True)
class Created: pass

@dataclass(frozen=True, slots=True)
class Invalid: pass

@dataclass(frozen=True, slots=True)
class Ok:
    config: Config

SetupResult = Created | Invalid | Ok

ERROR_MESSAGES = {
    ("portal", "ip"): "[portal.ip] Invalid or missing IP address. Please enter a valid IPv4 address (e.g., 192.168.16.41)",
    ("portal", "port"): "[portal.port] Invalid port number. It must be an integer between 1 and 65535",
    ("account", "username"): "[account.username] Username cannot be empty. Please fill it in the config file",
    ("account", "password"): "[account.password] Password cannot be empty. Please fill it in the config file",
    ("account", "isp"): "[account.isp] Invalid or missing ISP format. It must start with '@' followed by alphanumeric characters (e.g., @telecom, @cmcc, @xyw)",
}

def _create_config(config_path: Path) -> None:
    """Create config file."""

    doc = document()

    portal = table()
    portal.add(comment("认证门户的 IP 和端口号"))
    portal.add("ip", "192.168.16.41")
    portal.add("port", 801)
    doc.add("portal", portal)
    doc.add(nl())

    account = table()
    account.add(comment("请替换为你的学号和密码"))
    account.add("username", "20260101")
    account.add("password", "Password@123")
    account.add(nl())

    account.add(comment("互联网服务提供商后缀（根据实际学校宽带要求填写）"))
    account.add(comment("如中国电信(@telecom)、中国移动(@cmcc)、校园网(@xyw)"))
    account.add("isp", "@telecom")
    doc.add("account", account)

    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open("w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(doc))

    logger.info(f"[config] Generated config file at \"{config_path}\"")

def _load_config(config_path: Path) -> Config | None | Invalid:
    """Load config file."""

    if not config_path.exists():
        logger.warning(f"[config] Config file at \"{config_path}\" not found, will create one")
        return None

    try:
        with config_path.open("r", encoding="utf-8") as f:
            config = tomlkit.load(f)
    except Exception as e:
        logger.error(f"[config] TOML syntax error in config file at \"{config_path}\": error={e}")
        return Invalid()

    try:
        config_obj = Config(**config.unwrap())
    except ValidationError as e:
        logger.error(f"[config] Failed to parse config file at \"{config_path}\":")
        for error in e.errors():
            loc = error["loc"]
            msg = ERROR_MESSAGES.get(loc, error["msg"])
            logger.error(f"[config] {msg}")
        return Invalid()

    logger.info(f"[config] Loaded config file from \"{config_path}\"")
    return config_obj

def setup_config(config_path: Path) -> SetupResult:
    """Setup the config system, detect config file automatically, generate and load it."""

    result = _load_config(config_path)
    if result is None:
        _create_config(config_path)
        return Created()
    if isinstance(result, Invalid):
        return result
    return Ok(result)
