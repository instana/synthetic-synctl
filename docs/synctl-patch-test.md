# synctl patch test
The command `patch` can be used to updates selected attributes of a Synthetic test, only one attribute can be patched each time.

## Syntax
```
synctl patch test id [options]
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
    --custom-property <key>=<value>    set custom property, should be <key,value> pair
    
    --use-env, -e <name>               use a config hostname
    --host <host>                      set hostname
    --token <token>                    set token
    
```
### Options for API Simple tests
```
    --url <url>                        HTTP URL
    --follow-redirect <boolean>        set follow-redirect
    --mark-synthetic-call <boolean>    set markSyntheticCall
    --expect-status <int>              set expected HTTP status code
    --operation <method>               HTTP request methods, GET, POST, HEAD, PUT, etc.
    --validation-string <string>       set validation-string
```
### Options for API script test
```
    --script-file <file-name>          specify a script file to update APIScript or BrowserScript
    --bundle <bundle>                  set bundle content
    --entry-file <string>              entry file of a bundle test
```
### Options for Browser Script test
```
    --script-file <file-name>          specify a script file to update APIScript or BrowserScript
    --bundle <bundle>                  set bundle content
    --entry-file <string>              entry file of a bundle test
    --browser <string>                 browser type, support chrome and firefox
    --record-video <boolean>           enable/disable record video, false by default          
```
### Options for Webpage Simple Tests
```
    --url <url>                        HTTP URL
    --mark-synthetic-call <boolean>    set markSyntheticCall
    --record-video <boolean>           enable/disable record video, false by default
    --browser <string>                 browser type, support chrome and firefox
```
### Options for Webpage Script Tests
```
    --file,-f <file-name>              json payload
    --mark-synthetic-call <boolean>    set markSyntheticCall
    --record-video <boolean>           enable/disable record video, false by default
    --browser <string>                 browser type, support chrome and firefox
```
### Options for SSLCertificate Tests
```
    --hostname <host>                  set hostname for ssl test
    --port <int>                       set port 
    --remaining-days-check <int>       set days remaining before expiration of SSL certificate
```
## Examples
### Common Examples for All Tests
```
# Patch test label to simple-ping.
synctl patch test <synthetic-id> --label simple-ping

# Set test frequency to 5 min
synctl patch test <synthetic-id> --frequency 5

# Set test description to "New Description".
synctl patch test <synthetic-id> --description "New Description"

# Set test location id to id1, id2...
synctl patch test <synthetic-id> --lo <id1> <id2> ...

# Set test retries to 2
synctl patch test <synthetic-id> --retries 2

# Set test retry interval to 5, unit of retry interval is second.
synctl patch test <synthetic-id> --retry-interval 5

# Set test timeout to 120s
synctl patch test <synthetic-id> --timeout 120s

# Pause Synthetic test
synctl patch test <synthetic-id> --active false

# Set custom properties of a test
synctl patch test <synthetic-id> --custom-property key=value

# Set multiple custom properties of a test
synctl patch test <synthetic-id> --custom-property "key1=value1,key2=value2,key3=value3"
```

### Examples for API Simple tests
```
# Set URL of API Simple to `https://www.ibm.com`
synctl patch test <synthetic-id> --url https://www.ibm.com

# Set mark synthetic call to `True`.
synctl patch test <synthetic-id> --mark-synthetic-call True

# Set HTTP operation to POST
synctl patch test <synthetic-id> --operation POST

# Set follow redirect of API Simple to `true`
synctl patch test <synthetic-id> --follow-redirect true

# Set expect status of API Simple to 200
synctl patch test <synthetic-id> --expect-status 200

# Set validation string of API Simple to `synthetic-test`
synctl patch test <synthetic-id> --validation-string "synthetic-test"
```

### Examples for API Script tests
```
# Update synthetic test with new script
synctl patch test <synthetic-id> --script-file new-api-script.js

# Update bundle test with a zip file
synctl patch test <synthetic-id> --bundle synthetic.zip

# Update bundle test using base64 string
PATCH_BASE64_STR=`cat bundle.zip|base64`
synctl patch test <synthetic-id> --bundle "${PATCH_BASE64_STR}"

# Set entry file of bundle test
synctl patch test <synthetic-id> --entry-file bundle-test/index.js
```

### Examples for Browser Script tests
```
# Set browser to firefox
synctl patch test <synthetic-id> --browser firefox

# Set multiple custom properties of a test
synctl patch test <synthetic-id> --custom-property "key1=value1,key2=value2,key3=value3"
```
### Examples for Webpage Simple Tests
```
# Set URL of Webpage Simple to `https://www.ibm.com`
synctl patch test <synthetic-id> --url https://www.ibm.com

# Set browser to firefox
synctl patch test <synthetic-id> --browser firefox
```
### Examples for Webpage Script Tests
```
# Update synthetic test with new script
synctl patch test <synthetic-id> --script-file new-api-script.js

# Set record video true
synctl patch test <synthetic-id> --record-video true

# Set browser to firefox
synctl patch test <synthetic-id> --browser firefox
```
### Examples for SSLCertificate tests
```
# Set hostname of a SSLCertificate test
synctl patch test <synthetic-id> --hostname www.ibm.com

# Set port of a SSLCertificate test
synctl patch test <synthetic-id> --port 443

# Set remaining days of a SSLCertificate test
synctl patch test <synthetic-id> --remaining-days-check 30

