# Campus Network Autoauth

## Introduction

An auto-login script for `Dr.COM` campus network authentication.

> Tested on a campus network

## Requirements

- Python 3.13+
- `uv` package manager

## How to use

Optionally, copy `data/config.toml.example` to `data/config.toml`.

Write your username, password, and ISP to `data/config.toml`.

```text
usage: campus-network-autoauth [-c CONFIG] [-d] [-h] [-V]

An auto-login script for Dr.COM campus network authentication.

options:
  -c, --config CONFIG  Path to the config file
  -d, --debug          Enable debug mode
  -h, --help           Show this help message and exit
  -V, --version        Show the version number and exit
```

### Run the binary

Download the executable file for your OS and architecture from `Releases`, then:

```sh
./campus-network-autoauth
```

### Run the script

```sh
# sync dependencies
uv sync

# execute the script
uv run campus-network-autoauth
```

### Run the daemon

#### systemd + NetworkManager

Install the provided files:

```sh
# systemd unit
sudo install -m 644 daemon/systemd/campus-network-autoauth.service /etc/systemd/system/

# NetworkManager dispatcher hook
sudo install -m 755 -o root -g root \
    daemon/NetworkManager/99-campus-network-autoauth.sh \
    /etc/NetworkManager/dispatcher.d/
```

Before enabling, edit both files:

- `campus-network-autoauth.service` — set `WorkingDirectory` and `ExecStart` to your installation path.
- `99-campus-network-autoauth.sh` — adjust `CAMPUS_PATTERNS` to match your campus SSIDs (glob patterns supported).

Then enable the required services:

```sh
sudo systemctl enable --now NetworkManager-wait-online.service
sudo systemctl enable --now NetworkManager-dispatcher.service
sudo systemctl daemon-reload
sudo systemctl enable campus-network-autoauth.service
```

The unit runs once at boot with the network online. The dispatcher hook restarts it on every `up` event whose SSID matches — which also covers resume from suspend/hibernation, since the Wi-Fi link is re-established and `up` fires again.

Verify manually:

```sh
sudo /etc/NetworkManager/dispatcher.d/99-campus-network-autoauth.sh wlan0 up
systemctl status campus-network-autoauth.service
```

#### Windows Task Scheduler

...

## Build from source

Install the project non-editably before building so Nuitka can associate the
distribution metadata with the Python package. Use `--no-sync` with `uv run` to
preserve that installation mode:

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

## License

[MIT License](./LICENSE)
