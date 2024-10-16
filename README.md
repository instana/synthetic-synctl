# Synthetic CLI Command
The Synthetic CLI command `synctl` is used to manage Synthetic tests, locations, credentials and smart alert easily instead of Rest API.

# Table of Contents
- [Features](#features)
- [Prerequisites](#Prerequisites)
- [Installation](#installation)
- [Upgrade](#upgrade)
- [Configuration](#configuration)
- [Usage](#Usage)
- [Command List](#Command-List)

# Features
- Support multiple configurations of backend server.
- CRUD of Synthetic test, support API Simple, API Script, Browser Script, etc.
- Query/delete of Synthetic location.
- CRUD of Synthetic credential.
- CRUD of smart alert.
- Estimate PoP size and cost.

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
### Note : Version 2.0.0 introduces several changes that are not compatible with previous versions (1.x).

**Incompatible Options:**
- Option `--from-json` removed: Use the `-f, --from-file` option instead. The `-f, --from-file` option reads synthetic test payload from `.json` files.
- Option `--bundle-entry-file` replaces `--entry-file`: `--bundle-entry-file` option is now used to set entry file name of a bundle test.
- Option `--script` added: `--script` options reads different files according to their suffix, such as `.js`and `.side`.
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

# Usage

```
Usage: synctl <command> [options]

Options:
  -h, --help            show this help message and exit
  --version, -v         show version

Commands:
    config              manage configuration file
    create              create a Synthetic test, credential and smart alert
    get                 get Synthetic tests, locations, credentials, smart alert and pop-size
    patch               patch a Synthetic test
    update              update a Synthetic test and smart alert
    delete              delete Synthetic tests, locations credentials and smart alert

Use "synctl <command> -h/--help" for more information about a command.
```

# Command List
Command Configuration:
- [synctl config](docs/synctl-config.md) - Add configuration of Instana.

Synthetic test management:
- [synctl get test](docs/synctl-get-test.md) - Display Synthetic tests.
- [synctl create test](docs/synctl-create-test.md) - Create Synthetic tests.
- [synctl delete test](docs/synctl-delete-test.md) - Delete Synthetic tests.
- [synctl patch test](docs/synctl-patch-test.md) - Patch Synthetic test.
- [synctl update test](docs/synctl-update-test.md) - Update properties of Synthetic test.

Synthetic result management:
- [synctl get result](docs/synctl-get-result.md) - Display Synthetic test result.

Synthetic location management:
- [synctl get location](docs/synctl-get-loc.md) - Display Synthetic locations.
- [synctl delete location](docs/synctl-delete-loc.md) - Delete Synthetic locations.

Synthetic smart alert management:
- [synctl get alert](docs/synctl-get-alert.md) - Display smart alert.
- [synctl create alert](docs/synctl-create-alert.md) - Create smart alert.
- [synctl update alert](docs/synctl-update-alert.md) - Update properties of Smart Alert.
- [synctl delete alert](docs/synctl-delete-alert.md) - Delete smart alert.

Synthetic credential management:
- [synctl get/create/update/delete cred](docs/synctl-credential.md) - Manage credentials.

Others:
- [synctl get application](docs/synctl-get-app.md) - Display Instana application.
- [synctl get pop-cost](docs/synctl-get-cost.md) - Estimate cost of Instana hosted Synthetic POP.
- [synctl get pop-size](docs/synctl-get-size.md) - Estimate size of Self-hosted PoP.
