# synctl get test
List Synthetic test.

## Syntax
```
synctl get test [id] [options]
```

## Options
```
    -h, --help              show this help message and exit
    --verify-tls            verify tls certificate

    --type, -t <int>        Synthetic type, 0 HTTPAction, 1 HTTPScript, 2 BrowserScript, 3 WebpageScript, 4 WebpageAction, 5 SSLCertificate, 6 DNS
    --window-size <window>  set synthetic result window size, support [1,60]m, [1-24]h
    --save-script           save script to local, default is test label
    --show-script           output test script to terminal
    --show-details          output test script details to terminal
    --show-json             output test json to terminal
    --show-result           output latency and success rate
    --filter <filter>       filter test by application id or location id
    --CI-CD, --ci-cd        lists CI-CD tests
```

## Examples

### Display all tests
```
synctl get test
```

### Get test by Synthetic type

There are seven test type HTTPAction(0), HTTPScript(1), BrowserScript(2), WebpageScript(3), WebpageAction(4), SSLCertificate(5), and DNS(6) are supported.
In the command, it uses a number to represent a type for simple. They are:
  - 0 is API Simple
  - 1 is API Script
  - 2 is Browser Script
  - 3 is WebpageScript type
  - 4 is WebpageAction type
  - 5 is SSLCertificate type
  - 6 is DNS type

To get all API Simple test, specify the type 0:
```
synctl get test -t 0
```

### Get synthetic test result with time window, current support [1, 60]m, [1-24]h.

```
synctl get test --window-size 30m

synctl get test --window-size 6h
```

### Show a test details
```
synctl get test <id> --show-details
```

### Show latency and success rate of synthetic tests
```
synctl get test --show-result
```

### Show test configuration in json format
```
synctl get test <id> --show-json
```

### Show test script in console
```
synctl get test <id> --show-script
```

### Save test script to local, script is saved in current directory
```
synctl get test <id> --save-script
```

### Filter tests based on location id
```
synctl get test --filter=locationid=<locationId>
```

### Filer tests based on application id
```
synctl get test --filter=applicationid=<applicationId>
```

### Show all CI-CD tests
```
synctl get test --ci-cd
```

### Show a CI-CD test by a given test result id
```
synctl get test --result <result-id> --ci-cd
```