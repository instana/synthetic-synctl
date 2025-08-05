# synctl get location

Query and list Synthetic Locations.

## Syntax
```
synctl get location|lo [id] [options]
```

## Options
```
    -h, --help            show this help message and exit
    --verify-tls          verify tls certificate

    --show-details        output location details to console
    --show-json           output location json to terminal
```

## Examples

List Synthetic all locations
```
synctl get location
```

Show Synthetic location details
```
synctl get location <location-id> --show-details
```
Show location configuration in json format
```
synctl get location <location-id> --show-json
```
