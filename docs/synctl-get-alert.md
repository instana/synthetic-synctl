
# synctl get alert

Query and list Smart Alerts. 

## Syntax
```
synctl get alert [id] [options]
```

## Options
```
    -h, --help             show this help message and exit
    --show-details         output alert details to terminal
    --show-json            output alert json to terminal

    -e, --use-env <name>   use a specified config
    --host <host>          set hostname
    --token <token>        set token
```

## Examples
Get Smart Alert
```
synctl get alert
```

Show smart alert details.
```
synctl get alert <id> --show-details
```

Show smart alert payload in json format.
```
synctl get alert <id> --show-json
```
