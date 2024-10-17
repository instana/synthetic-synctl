# synctl get datacenter
List Synthetic datacenter

## Syntax
```
synctl get datacenter [id] [options]
```

## Options
```
    -h, --help              show this help message and exit
    --verify-tls            verify tls certificate

    --show-details          output datacenter details to terminal
    --show-json             output datacenter json to terminal
```

## Examples

### Display all datacenters
```
synctl get datacenter
```
### Show a datacenter details
```
synctl get datacenter <id> --show-details
```

### Show datacenter configuration in json format
```
synctl get datacenter <id> --show-json
```