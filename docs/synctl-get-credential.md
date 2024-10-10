# synctl get cred
List Synthetic credential.

## Syntax
```
synctl get cred [cred-name] [options]
```

## Options
```
    -h, --help            show this help message and exit
    --verify-tls          verify tls certificate
    
    --show-details        output cred details to terminal
```
### Display all credentials
```
synctl get cred
```

### Display all credential details
```
synctl get cred --show-details
```

### Display a credential details
```
synctl get cred <cred-name> --show-details
```
