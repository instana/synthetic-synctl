# synctl config

Add Instana Backend Configuration of `synctl`,it support three types of configurations:
- Use configuration file, default configuration file is under `~/.synthetic/config.json`.
- Use options `--host` and `--token` to specify the host and token.
- Use environment variables `SYN_SERVER_HOSTNAME`, `SYN_API_TOKEN`.

**Note:** The priority of configuration is command options > environment variables > configuration file.

## Syntax
```
synctl config {set,list,use,remove} [options]
```

## Options

```
    -h, --help            show this help message and exit

    --host <host>         set hostname
    --token, -t <token>   set token
    --show-token          show token
    --env, --name <name>  specify which config to use
    --default             set configuration as default
```

## Examples

### Configure Instana

Configure your instana with host and token, and an alias name is needed, if you have multiple instana, you can choose them by name. `--default` is to set current as default.
```
synctl config set \
    --host "https://test-instana.pink.instana.rocks" \
    --token "Your Token" \
    --name "pink" \
    --default
```

List configurations
```
synctl config list
```

Show configuration token
```
synctl config list --show-token
```

#### Set a configuration as default.
```
synctl config use --name pink --default
```

#### Remove a configuration.
```
synctl config remove --name pink
```
**Note:** By default, configuration file is under `~/.synthetic/config.json`.

### Run command with options --host <host> and --token <token>

Get all tests with options
```
synctl get test --host "https://test-instana.pink.instana.rocks" --token <Your-Token>
```

Get all locations with options
```
synctl get location --host "https://test-instana.pink.instana.rocks" --token <Your-Token>
```

### Use environment variables SYN_SERVER_HOSTNAME and SYN_API_TOKEN.

```
export SYN_SERVER_HOSTNAME="https://test-instana.pink.instana.rocks"
export SYN_API_TOKEN="Your Token"

# then run command with no options
synctl get test

# retrieve all location
synctl get location
```
