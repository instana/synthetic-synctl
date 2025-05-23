# synctl update test

Update Synthetic test properties.

## Syntax
```
synctl update test <id> [options]
```

## Options

### Common options
```
    -h, --help                                         show this help message and exit
    --verify-tls                                       verify tls certificate

    --active <boolean>                                 set active
    --frequency <int>                                  set frequency
    --location <id> [<id> ...]                         set location
    --description <string>                             set description
    --label <string>                                   set label
    --retries <int>                                    set retries, min is 0 and max is 2
    --retry-interval <int>                             set retry-interval, min is 1, max is 10
    --timeout <num>ms|s|m                              set timeout, accept <number>(ms|s|m)
    -f, --from-file <file>                             load synthetic test payload from file (.json)
    --custom-properties <key>=<value>                  set custom property, should be <key,value> pair
    --app-id, --application-id <id>                    set application id
    --apps, --applications [<id> ...]                  set multiple applications
    --websites [<id> ...]                              set websites
    --mobile-apps, --mobile-applications [<id> ...]    set mobile appliactions
    
    --use-env, -e <name>                               use a config hostname
    --host <host>                                      set hostname
    --token <token>                                    set token
```

### Options for API Simple test
```
    --operation <method>               HTTP request methods, GET, POST, HEAD, PUT, etc.
    --mark-synthetic-call <boolean>    set markSyntheticCall
    --url <url>                        HTTP URL
    --headers <json>                   HTTP headers
    --body <string>                    HTTP body
    --follow-redirect <boolean>        set follow-redirect
    --expect-status <int>              set expected HTTP status code
    --validation-string <string>       set validation-string
    --expect-status <int>              expected status code, Synthetic test will fail if response status is not equal to it, default 200
    --expect-json <string>             An optional object to be used to check against the test response object
    --expect-match <string>            An optional regular expression string to be used to check the test response
    --expect-exists <string>           An optional list of property labels used to check if they are present in the test response object
    --expect-not-empty <string>        An optional list of property labels used to check if they are present in the test response object with a non-empty value
    --allow-insecure <boolean>         if set to true then allow insecure certificates
```

### Options for API Script test
```
    --script <file>                    load script (.js) from file
    --bundle <bundle>                  Synthetic bundle test script, support zip file (.zip) path or zip file content encoded with base64
    --bundle-entry-file <file-name>    Synthetic bundle test entry file, e.g, myscript.js
    --mark-synthetic-call <boolean>    set markSyntheticCall
```

### Options for Browser Script test
```
    --script <file>                    load script (.js) from file
    --mark-synthetic-call <boolean>    set markSyntheticCall
    --bundle <bundle>                  Synthetic bundle test script, support zip file (.zip) path or zip file content encoded with base64
    --bundle-entry-file <file-name>    Synthetic bundle test entry file, e.g, myscript.js
    --record-video <boolean>           enable/disable record video, false by default
    --browser <string>                 browser type, support chrome and firefox
```

### Options for Webpage Simple test
```
    --url <url>                        HTTP URL
    --mark-synthetic-call <boolean>    set markSyntheticCall
    --record-video <boolean>           enable/disable record video, false by default
    --browser <string>                 browser type, support chrome and firefox
```

### Options for Webpage Script test
```
    --script <file>                    load script (.side) from file
    --mark-synthetic-call <boolean>    set markSyntheticCall
    --record-video <boolean>           enable/disable record video, false by default
    --browser <string>                 browser type, support chrome and firefox
```

### Options for SSLCertificate test
```             
    --hostname  <host>                 set hostname for ssl test
    --port <int>                       set port 
    --remaining-days-check <int>       set days remaining before expiration of SSL certificate
```

### Options for DNS test
```
    --cname <boolean>                  enable the canonical name in the DNS response, false by default
    --lookup <host>                    set the name or IP address of the host
    --lookup-server-name <boolean>     enable recursive DNS lookups, false by default
    --port <int>                       set port, default is 53
    --query-time <string>              an object with name/value pairs used to validate the test response time
    --query-type <string>              DNS query type: Value must be one of ALL, ALL_CONDITIONS, ANY, A, AAAA, CNAME, NS. Default value is A
    --recursive-lookups <boolean>      enables recursive DNS lookups, false by default
    --server <string>                  set IP address of the DNS server
    --server-retries <int>             set number of times to try a timed-out DNS lookup before returning failure. Default is 1
    --target-values <str>              set list of filters to be used to validate the test response
    --transport <str>                  set protocol used to do DNS check. Only UDP is supported
```

## Examples
### Common Example for All tests
```
# Update a Synthetic test with multiple options.
synctl update test <synthetic-id> \
    --frequency 5 \
    --label "simple-ping" \
    --location <id1> <id2> ... \
    --retry-interval 3 \
    --follow-redirect true \
    --validation-string "a synthetic test" \
    --expect-status 200 \
    --custom-properties "key1=value1,key2=value2"
```

### Example for API Simple test
```
synctl update test <synthetic-id> \
    --url https://www.ibm.com \
    --expect-status 200
```

Expect json example
```
synctl update <synthetic-id> \
    --expect-json '{
      "slideshow": {
        "author": "Yours Truly",
        "date": "date of publication",
        "slides": [
          {
            "title": "Wake up to WonderWidgets!",
            "type": "all"
          },
          {
            "items": [
              "Why <em>WonderWidgets</em> are great",
              "Who <em>buys</em> WonderWidgets"
            ],
            "title": "Overview",
            "type": "all"
          }
        ],
        "title": "Sample Slide Show"
      }
    }'
```
Update test with expect-match

```
synctl update test <synthetic-id> \
    --expect-match ibm
```
Update test with expect-exists
```
synctl update test <synthetic-id> \
    --expect-exists '["slideshow"]'
```
Update test with expect-not-empty
```
synctl update test <synthetic-id> \
    --expect-not-empty '["slideshow"]'
```

### Example for API Script test
```
#  Update a test with json payload.
1. Get synthetic configuration and save to test.json
    synctl get test <synthetic-id> --show-json > test.json

2. edit json file and update test.
    synctl update test <synthetic-id> --from-file/-f test.json

```

### Example for Browser Script test
```
synctl update test <synthetic-id> \
    --mark-synthetic-call false \
    --script script.js
```

### Example for Webpage Simple test
```
synctl update test <synthetic-id> \
    --url https://www.ibm.com \
    --record-video true
```

### Example for Webpage Script test
```
synctl update test <synthetic-id> \
    --mark-synthetic-call false \
    --browser firefox
```

### Example for SSLCertificate test
```
synctl update test <synthetic-id> \
    --hostname www.ibm.com \
    --remaining-days-check 120
```

### Example for DNS test
```
synctl update test <synthetic-id> \
    --lookup www.ibm.com \
    --cname true \
    --lookup-server-name false \
    --query-type ANY \
    --recursive-lookups true \
    --server 8.8.8.8 \
    --server-retries 1 \
    --port 53  \
    --transport UDP \
    --query-time '{"key": "responseTime", "operator": "LESS_THAN", "value": 120}' \
    --target-values '{"key": "CNAME", "operator": "NOT_MATCHES", "value": "test"}'
```