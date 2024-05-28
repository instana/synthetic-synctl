# synctl create alert 

Create Synthetic Smart alert.

## Syntax
```
synctl create alert [options]
```

## Options
```
    -h, --help                        show this help message and exit

    --test id [id ...]                Synthetic test id, support multiple Synthetic tests id
    --name <string>                   friendly name of the Smart Alerts
    --description, -d <string>        the description of Smart Alerts
    --severity <string>               the severity of alert is either warning or critical
    --alert-channel <id>              alerting channel
    --violation-count <int>           the number of consecutive failures to trigger an alert
    --tag-filter-expression <json>    tag filter expression
```

## Examples

Create Smart Alert for Synthetic test
```
synctl create alert --name "Smart-alert" \
       --alert-channel "$ALERT_CHANNEL" \
       --test "$SYNTHETIC_TEST" \
       --violation-count 2
```

Schedule a smart alert for multiple Synthetic tests
```
synctl create alert --name "Smart-alert" \
       --alert-channel "$ALERT_CHANNEL" \
       --test "$SYNTHETIC_TEST1" "$SYNTHETIC_TEST2" "$SYNTHETIC_TEST3" ...  \
       --violation-count 2
```

Create alert with tag filter expression
```      
synctl create alert --name "smart alert" \
        --test "$SYNTHETIC_TEST1" "$SYNTHETIC_TEST2"... \
        --alert-channel "$ALERT_CHANNEL" \
        --severity critical \
        --violation-count 3 \
        --tag-filter-expression '{"type": "EXPRESSION", "logicalOperator": "AND", "elements": []}'
```

**Note:** To get alert channel, use command `synctl get alert-channel`.
