# synctl patch credential
The command `patch` can be used to update selected attributes of a Synthetic credential, only one attribute can be patched each time.

## Syntax
```
synctl patch cred <cred-name> [options]
```

## Options

### Common options
```
    -h, --help                         show this help message and exit
    --verify-tls                       verify tls certificate

    --apps, --applications [<id> ...]  set multiple applications
    --websites <id> [<id> ...]         set websites
    --mobile-apps <id> [<id> ...]      set mobile appliactions
```
## Examples
### Patch a Synthetic credential with multiple applications.
```
synctl patch cred <cred-name> --applications/--apps "$APPLICATION1" "$APPLICATION2" "$APPLICATION3" ..."
```
### Patch a Synthetic credential with multiple websites.
```
synctl patch cred <cred-name> --websites "$WEBSITE1" "$WEBSITE2" ...
```
### Patch a Synthetic credential with multiple mobile applications.
```
synctl patch cred <cred-name> --mobile-applications/--mobile-apps "$APPLICATION1" "$APPLICATION2" "$APPLICATION3" ..."
```