# synctl create credential

Create Synthetic credential.

## Syntax
```
synctl create cred [options]
```

## Options
### Common options
```
    -h, --help                                  show this help message and exit
    --verify-tls                                verify tls certificate

    --apps, --applications <id>                 set application id
    --mobile-apps, --mobile-applications <id>   set mobile apllication id
    --websites <id>                             set websites
```
## Examples
### Create a credential

```
synctl create cred --key <key-name> --value <value>
```

### Create a credential with applications
```
synctl create cred --key <key-name> --value <value> --apps "$APPLICATION1" "$APPLICATION2" "$APPLICATION3" ...
```

### Create a credential with WEBSITES
```
synctl create cred --key <key-name> --value <value> --websites "$WEBSITE1" "$WEBSITE2" ...
```