# Synthetic CLI Command
Synthetic Command Line Tool(synctl) is used to manage synthetic tests, locations and credentials.

# Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Upgrade](#upgrade)
- Synthetic Test
    - List test
    - Create Synthetic Test
    - Update test
    - Patch Test
    - Delete Test
- Synthetic Locations
    - List locations
    - Delete locations
- Smart Alert
    - list
    - create
    - update
- List Test Result
- Manage Credential
- Application
- Synthetic POP Size
- Synthetic POP Cost

# Features
- CRUD of Synthetic test, support API Simple, API Script, Browser Script, etc.
- Query/delete of Synthetic location.
- Query/create/update/delete of Synthetic credential.
- Support multiple configurations of backend server.
- CRUD of Smart alerts.

# Prerequisites
- [Python 3.6+](https://www.python.org/downloads/)

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

# Configure an Instana Backend
`synctl` support three types of configurations:
- Use configurations file, the default config file is under `~/.synthetic/config.json`.
- Use `--host` and `--token` options to specify the host and token.
- Set environment variables before run synctl command, `SYN_SERVER_HOSTNAME`, `SYN_API_TOKEN` are used to store host and token.

**Note:** The priority of configuration is command options > environment variables > config file.

### Create a token
1. Log in to the Instana UI. 
2. Navigate to the `Settings` page, go to the `API Tokens` tab under Team Settings.
3. Click on `New API Token` in the upper right corner to create a new token with proper permissions.

### Use a configuration file (Recommended)
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
# set SYN_SERVER_HOSTNAME and SYN_API_TOKEN
export SYN_SERVER_HOSTNAME="https://test-instana.pink.instana.rocks"
export SYN_API_TOKEN="Your Token"

# then run command with no options
# retrieve all tests
synctl get test

# retrieve all location
synctl get location
```

# Manage configuration files
`synctl config` can be used to manage configuration files.  

### synctl config Syntax
```
synctl config {set,list,use,remove} [options]

# commands
set        configure a new backend server
list       list all configurations
use        modify a configuration
remove     delete a configuration
```

### synctl config Options
```
-h, --help            show this help message and exit
--host <host>         set hostname
--token, -t <token>   set token
--env, --name <name>  specify which config to use
--default             set as default
```

### synctl config Examples

```
# configure a backend, name it as pink and set it as default
synctl config set \
    --host "https://test-instana.pink.instana.rocks" \
    --token "Your Token" \
    --name "pink" \
    --default

# set pink as default
synctl config use --name pink --default

# remove a config
synctl config remove --name pink
```

