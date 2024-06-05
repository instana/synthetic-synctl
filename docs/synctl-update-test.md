# synctl update test

Update Synthetic test properties.

## Syntax
```
synctl update test <id> [options]
```

## Options

### Common options
```
    -h, --help                         show this help message and exit

    --active <boolean>                 set active
    --frequency <int>                  set frequency
    --location <id> [<id> ...]         set location
    --description <string>             set description
    --label <string>                   set label
    --retries <int>                    set retries, min is 0 and max is 2
    --retry-interval <int>             set retry-interval, min is 1, max is 10
    --timeout <num>ms|s|m              set timeout, accept <number>(ms|s|m)
    --custom-properties <key>=<value>  set custom property, should be <key,value> pair
    --app-id, --application-id <id>    set application id
    
    --use-env, -e <name>               use a config hostname
    --host <host>                      set hostname
    --token <token>                    set token
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
    -f, --from-file <file-name>        specify a script file to update API/Browser script(.js/.side), or json payload(.json)
    --bundle <bundle>                  set bundle content
    --bundle-entry-file <string>       entry file of a bundle test
    --mark-synthetic-call <boolean>    set markSyntheticCall
```

### Options for Browser Script test
```
    -f, --from-file <file-name>        specify a script file to update API/Browser script(.js/.side), or json payload(.json)
    --mark-synthetic-call <boolean>    set markSyntheticCall
    --bundle <bundle>                  set bundle content
    --bundle-entry-file <string>       entry file of a bundle test
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
    -f, --from-file <file-name>        specify a script file to update API/Browser script(.js/.side), or json payload(.json)
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
    --from-file script.json
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
