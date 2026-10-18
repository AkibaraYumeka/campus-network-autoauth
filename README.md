# Campus Network Autoauth

## Introduction

An auto-login script for `Dr.com` campus network authentication.

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

...

## License

[MIT License](./LICENSE)
