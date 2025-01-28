# synctl get metric
List Synthetic metrics.

## Syntax
```
synctl get metric [options]
```

## Options
```
    -h, --help                          show this help message and exit
    --verify-tls                        verify tls certificate

    --metric <json>                     set metrics
    --tag <json>                        set the tag for grouping the data
    --tag-filter-expression <json>      tag filter expression
```

## Examples
synctl get metric --metric '{"aggregation": "MEAN", "metric": "synthetic.metricsResponseTime"}' \
    --tag '{"groupbyTag": "synthetic.applicationId"}' \
    --tag-filter-expression '{"type": "EXPRESSION", "logicalOperator": "AND", "elements": []}'