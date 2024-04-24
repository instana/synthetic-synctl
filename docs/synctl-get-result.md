# synctl get result
Query Synthetic test results

## Syntax
```
synctl get result [id] [options]
```

### Options
```
    -h, --help               show this help message and exit
    --test                   Synthetic test id
    --window-size <window>   set synthetic result window size, support [1,60]m, [1-24]h
    --har                    save HAR to local
    --use-env, -e <name>     use a specified config
    --host <host>            set hostname
    --token <token>          set token
```

## Examples

Display result list with time window, default time window is 1h.
```
synctl get result --test <test-id> --window-size 30m
```


Show result details, note that time window need to be same with result list.
```
synctl get result <id> --test <test-id> --window-size 6h
```

Save HAR to local
```
synctl get result <id> --test <test-id> --har
```