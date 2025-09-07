# synctl update alert

## Syntax
```
synctl update alert <id> [options]
```

## Options
```
    -h, --help                          show this help message and exit
    --verify-tls                        verify tls certificate

    --from-file,-f <file-name>          json payload
    --test id [id ...]                  synthetic-test id, support multiple synthetic tests id
    --name <string>                     friendly name of the Smart Alerts
    --description, -d <string>          the description of Smart Alerts
    --severity <string>                 the severity of alert is either warning or critical
    --alert-channel <id>                alerting channel
    --violation-count <int>             the number of consecutive failures to trigger an alert
    --tag-filter-expression <json>      tag filter expression
    --custom-payloads <json>            additional information in the alert notifications
    --grace-period <str>                duration for which an alert remains open after conditions are no longer violated. Support: [1-60]m, [1-24]h, [1-7]d.
    --enable                            enable smart alert
    --disable                           disable smart alert

    --use-env, -e <name>                use a config hostname
    --host <host>                       set hostname
    --token <token>                     set token
```

## Examples

Update a smart alert with multiple options
```
synctl update alert <alert-id> --name "Smart-alert" \
    --alert-channel "$ALERT_CHANNEL1" "$ALERT_CHANNEL2" "$ALERT_CHANNEL3" ... \
    --test "$SYNTHETIC_TEST1" "$SYNTHETIC_TEST2" "$SYNTHETIC_TEST3" ... \
    --violation-count 2 \
    --severity warning
```

Update a smart alert with json file.

```
# get smart alert configuration and save to alert.json
synctl get alert <alert-id> --show-json > alert.json

# edit json file and update
synctl update alert <alert-id> --from-file/-f alert.json
```

Update a smart alert with `--tag-filter-expression` option
```
synctl update alert <alert-id> --tag-filter-expression '{"type": "EXPRESSION", "logicalOperator": "AND", "elements": []}'
```
Update a smart alert with custom payloads
```
synctl update alert <alert-id> --custom-payloads '[{"type": "staticString", "key": "test", "value": "12345"}]'
```
Update a smart alert with multiple custom payloads
```
synctl update alert <alert-id> --custom-payloads '[{"type": "staticString", "key": "key1", "value": "value1"},{"type": "staticString", "key": "key2", "value": "value2"}]'
```
Update a smart alert with grace period in hours
```
synctl update alert <alert-id> --grace-period 3h
```
Update a smart alert with grace period in days
```
synctl update alert <alert-id> --grace-period 5d
```

Enable a smart alert
```
synctl update alert <alert-id> --enable
```

Disable a smart alert.
```
synctl update alert <alert-id> --disable
```
