# Synthetic CLI Command
Synthetic Command Line Tool(synctl) is used to manage synthetic tests, locations, credentials and smart alert.

# Table of Contents
- [Features](#features)
- [Synthetic CLI Documentation](docs/synctl-cli.md)
- [Prerequisites](#Prerequisites)
- [Installation](#installation)
- [Upgrade](#upgrade)
- [Configuration](#configuration)

# Features
- CRUD of Synthetic test, support API Simple, API Script, Browser Script, etc.
- Query/delete of Synthetic location.
- Query/create/update/delete of Synthetic credential.
- Support multiple configurations of backend server.
- CRUD of Smart alerts.

# Prerequisites
- [Python 3.6+](https://www.python.org/downloads/)
- [pip3](https://pip.pypa.io/en/stable/installation/)

# Installation
If you have installed synctl(version 1.0.x) before, make sure remove it via `rm /usr/local/bin/synctl`. 
```
pip3 install synctl
```

**Note:** To install python3 on Windows, see [Python](https://www.python.org/downloads/windows/).

# Upgrade
Upgrade `synctl` to latest version.
```
pip3 install --upgrade synctl
```

Upgrade `synctl` to a specified version.
```
pip3 install --upgrade synctl==<version>
```

# Configuration

`synctl` support three types of configurations:
- Use configurations file, the default config file is under `~/.synthetic/config.json`.
- Use `--host` and `--token` options to specify the host and token.
- Set environment variables before run synctl command, `SYN_SERVER_HOSTNAME`, `SYN_API_TOKEN` are used to store host and token.

**Note:** The priority of configuration is command options > environment variables > config file.

### Create a token
1. Log in to the Instana UI. 
2. Navigate to the `Settings` page, go to the `API Tokens` tab under Team Settings.
3. Click on `New API Token` in the upper right corner to create a new token with proper permissions.

### Add a configuration
The configuration file is stored under `~/.synthetic/config.json` by default, uses can edit it directly or use `synctl config` command to manage configuration information. Below is an example to configure a backend server:
```
# set your backend host and token, and give it an alias name, and set it as default
synctl config set \
    --host "https://test-instana.pink.instana.rocks" \
    --token "Your Token" \
    --name "pink" \
    --default

# list configurations
synctl config list
```
**Note:** By default, config file is `~/.synthetic/config.json`.

### Use command options
Synthetic `synctl` command can accept `--host <host>` and `--token <token>` option to specify host and token if there is not a configuration file. See below examples:

```
# retrieve all tests with --host and --token
synctl get test --host "https://test-instana.pink.instana.rocks" --token <Your-Token>

# get all locations with host and token
synctl get location --host "https://test-instana.pink.instana.rocks" --token <Your-Token>
```

### Use environment variables

```
export SYN_SERVER_HOSTNAME="https://test-instana.pink.instana.rocks"
export SYN_API_TOKEN="Your Token"
```

After export the variables then command can be run without any options.
