# 校园网自动登录

## 简介

一个用于 `Dr.COM` 校园网认证的自动登录脚本。

> 已在某使用 Dr.COM 认证的校园网环境下测试通过。

> [!WARNING]
> 本项目仅为个人学习用途。
> **使用前请务必先了解清楚学校的网络政策**
> ——自动化登录工具可能违反校园网管理规定，后果自负

## 环境要求

- Python 3.13+
- `uv` 包管理器

## 使用方法

可选：将 `data/config.toml.example` 复制为 `data/config.toml`。

然后在 `data/config.toml` 中填入你的用户名、密码和运营商。

```text
usage: campus-network-autoauth [-c CONFIG] [-d] [-h] [-V]

An auto-login script for Dr.COM campus network authentication.

options:
  -c, --config CONFIG  Path to the config file
  -d, --debug          Enable debug mode
  -h, --help           Show this help message and exit
  -V, --version        Show the version number and exit
```

### 运行可执行文件

从 `Releases` 页面下载对应操作系统和架构的可执行文件，运行：

```sh
./campus-network-autoauth
```

### 运行脚本

```sh
# 同步依赖
uv sync

# 运行脚本
uv run campus-network-autoauth
```

### 以守护进程方式运行

#### systemd + NetworkManager

安装项目提供的文件：

```sh
# systemd 服务单元
sudo install -m 644 daemon/systemd/campus-network-autoauth.service /etc/systemd/system/

# NetworkManager 事件钩子
sudo install -m 755 -o root -g root \
    daemon/NetworkManager/99-campus-network-autoauth.sh \
    /etc/NetworkManager/dispatcher.d/
```

启用前请先编辑这两个文件：

- `campus-network-autoauth.service` —— 将 `WorkingDirectory` 和 `ExecStart` 选项改为你的实际安装路径。
- `99-campus-network-autoauth.sh` —— 调整 `CAMPUS_PATTERNS` 以匹配你学校的 Wi-Fi 名称（支持 glob 通配符）。

启用相关服务：

```sh
sudo systemctl enable --now NetworkManager-wait-online.service
sudo systemctl enable --now NetworkManager-dispatcher.service
sudo systemctl daemon-reload
sudo systemctl enable campus-network-autoauth.service
```

服务单元会在开机联网后运行一次。事件钩子则会在每次 SSID 匹配的 `up` 事件发生时重启该服务——这也顺便覆盖了从休眠/睡眠恢复的情况，因为 Wi-Fi 链路重新建立时会再次触发 `up` 事件。

手动验证：

```sh
sudo /etc/NetworkManager/dispatcher.d/99-campus-network-autoauth.sh wlan0 up
systemctl status campus-network-autoauth.service
```

#### Windows 任务计划程序

计划任务的安装和卸载通过 `daemon/WindowsTaskScheduler/` 下的辅助脚本完成，两者都需要**以管理员权限（UAC 提权）运行**：

- 右键点击 `install.bat` -> **以管理员身份运行**，或在管理员命令提示符中执行：`daemon\WindowsTaskScheduler\install.bat`

之所以需要提权，只是为了在任务计划策略较严格的系统上让 `schtasks /Create` 和 `schtasks /Delete` 能正常执行。任务本身以 `LeastPrivilege` 注册、以当前用户身份运行——**不会**以管理员权限运行。

脚本会自动定位 `campus-network-autoauth.exe`，读取当前用户的 SID，填充 `task.xml.template`，然后注册一个名为 `CampusNetworkAutoauth` 的计划任务。触发条件为：开机、登录和会话解锁。

如果可执行文件不在脚本旁边或仓库根目录下，请显式指定路径：

```sh
install.bat -ExePath "X:\app\campus-network-autoauth.exe"
```

卸载时，右键点击 `uninstall.bat` -> **以管理员身份运行**。

手动验证：

```sh
schtasks /Query /TN CampusNetworkAutoauth /V /FO LIST
schtasks /Run /TN CampusNetworkAutoauth
```

> 注意：由于任务以 `InteractiveToken` 方式运行，`BootTrigger` 只有在存在用户会话时才会触发。大多数场景下真正起作用的是 `LogonTrigger` 和 `SessionUnlock`；后者也覆盖了从睡眠恢复的情况，因为解锁会重新启动该任务。

## 从源码构建

构建前请先以非可编辑模式安装项目，这样 Nuitka 才能将发行版元数据与 Python 包关联起来。使用 `uv run` 时加上 `--no-sync` 以保持该安装模式：

```sh
uv sync --group dev --no-editable
uv run --no-sync python -m nuitka \
    --include-distribution-metadata=campus-network-autoauth \
    --onefile \
    --output-dir=dist \
    --output-filename=campus-network-autoauth \
    --assume-yes-for-downloads \
    --python-flag=-m \
    --nofollow-import-to="*.tests" \
    --nofollow-import-to="*.distutils" \
    --nofollow-import-to=unittest \
    --nofollow-import-to=pytest \
    --nofollow-import-to=setuptools \
    src/campus_network_autoauth
```

## 许可证

[MIT License](./LICENSE)
