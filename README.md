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

### Run the binary

...

### Run the script

```sh
# sync dependencies
uv sync

# execute the script
uv run campus-network-autoauth
```

## Build from source

Install the project non-editably before building so Nuitka can associate the
distribution metadata with the Python package. Use `--no-sync` with `uv run` to
preserve that installation mode:

```sh
uv sync --group dev --no-editable
uv run --no-sync python -m nuitka --include-distribution-metadata=campus-network-autoauth --onefile --output-dir=dist --output-filename=campus-network-autoauth --assume-yes-for-downloads --python-flag=-m --nofollow-import-to="*.tests" --nofollow-import-to="*.distutils" --nofollow-import-to=unittest --nofollow-import-to=pytest --nofollow-import-to=setuptools src/campus_network_autoauth
```

## License

[MIT License](./LICENSE)
