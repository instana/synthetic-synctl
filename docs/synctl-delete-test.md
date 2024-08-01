# synctl delete test

Delete Synthetic test.

## Syntax
```
synctl delete test [id...] [options]
```

## Options
``` 
    -h, --help            show this help message and exit
    --verify-tls          verify tls certificate

    --match-regex <regex> use a regex to match synthetic label
    --match-location <id> delete tests match this location id
    --no-locations        delete tests with no locations

    --use-env, -e <name>  specify a config name
    --host <host>         set hostname
    --token <token>       set token
```

## Examples

Delete Synthetic with id
```
synctl delete test <synthetic-id>
```

Delete several Synthetic tests
```
synctl delete test <id-1> <-id-2> <id-3> ...
```

Delete test whose label match regex, refer [regular expression operations](https://docs.python.org/3/library/re.html). Delete all tests which label match regex `^ping-test-*`
```
synctl delete test --match-regex "^ping-test-*"
```

Delete all tests
```
synctl delete test --match-regex ".*"
```

Delete all tests with <location-id>, it will not delete tests with multiple locations. For example, `synctl delete test --match-location A` will not delete test with location [A, B]
```
synctl delete test --match-location <location-id>
```

Delete all tests whose locations are empty
```
synctl delete test --no-locations
```
