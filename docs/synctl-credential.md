# Manage Credentials

Manage Synthetic credentials.

## Options
```
    -h, --help            show this help message and exit
    --verify-tls          verify tls certificate
```
### Display all credentials
```
synctl get cred
```

### Create a credential

```
synctl create cred --key <key-name> --value <value>
```

### Update a credential

```
synctl update cred <cred-name> --value <value>
```

### Delete a credential

```
synctl delete cred <key-name>
```
