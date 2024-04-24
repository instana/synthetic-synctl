# Config an Instana Backend
`synctl` support three types of configurations:
- Use configurations file, default is `~/.synthetic/config.json`.
- Use `--host` and `--token` to specify the host and token.
- Use environment variables, export `SYN_SERVER_HOSTNAME`, `SYN_API_TOKEN`.

**Note:** The priority of configuration is command options > environment variables > config file.

### Use a config file (Recommended)

```
# set your backend host and token, and give it an alias name, and set it as default
synctl config set \
    --host "https://test-instana.pink.instana.rocks" \
    --token "Your Token" \
    --name "pink" \
    --default

# list configs
synctl config list

# set pink as default
synctl config use --name pink --default

# remove a config
synctl config remove --name pink
```
**Note:** By default, config file is `~/.synthetic/config.json`.

### Run command with --host <host> and --token <token>

```
# retrieve all tests with --host and --token
synctl get test --host "https://test-instana.pink.instana.rocks" --token <Your-Token>

# get all locations with host and token
synctl get location --host "https://test-instana.pink.instana.rocks" --token <Your-Token>
```

### Use environment vars

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
