from pathlib import Path

import tomlkit
from tomlkit import document, comment, nl

# TODO: check config

def create_config(path: Path) -> tomlkit.TOMLDocument:
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

    with path.open("w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(doc))

    return doc

def load_config(path: Path) -> tomlkit.TOMLDocument:
    with path.open("r", encoding="utf-8") as f:
        return tomlkit.parse(f.read())
