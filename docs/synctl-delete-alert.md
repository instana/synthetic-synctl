# synctl delete alert

Delete Synthetic smart alert.

## Syntax
```
synctl delete alert [id...] 
```
## Options
```
    -h, --help            show this help message and exit
    --verify-tls          verify tls certificate
```

## Examples

Delete a smart alert
```
synctl delete alert <alert-id>
```

Delete several smart alerts
```
synctl delete alert <alert-id-1> <alert-id-2> <alert-id-3> ...
```
