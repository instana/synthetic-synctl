# synctl run test

Run a test on-demand

## Syntax
```
synctl run test <id> [options]
```

## Options
```
    --location id [id ...]                      location id, support multiple locations id
    --retries <int>                             retry times, value is from [0, 2]
    --retry-interval <int>                      retry interval, range is [1, 10]
    --timeout <num>ms|s|m                       set timeout, accept <number>(ms|s|m)
    --custom-properties <string>                An object with name/value pairs to provide additional information of the Synthetic test

    --use-env <name>, -e <name>                 use a specified configuration
    --host <host>                               set hostname
    --token <token>                             set token
```

## Examples  

### Run a test
```
synctl run test <test-id>  --location "$LOCATION"
```

### Run a test with retries
```
synctl run test <test-id>  --location "$LOCATION" --retries 2
```

### Run a test with custom properties
```
synctl run test <test-id>  --location "$LOCATION" --custom-properties "key1=value1,key2=value2"
```