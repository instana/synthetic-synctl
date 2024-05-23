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
    --custom-property <key>=<value>    set custom property, should be <key,value> pair
    
    --use-env, -e <name>               use a config hostname
    --host <host>                      set hostname
    --token <token>                    set token
```
### Options for API Simple Tests
```
    --operation <method>               HTTP request methods, GET, POST, HEAD, PUT, etc.
    --mark-synthetic-call <boolean>    set markSyntheticCall
    --url <url>                        HTTP URL
    --follow-redirect <boolean>        set follow-redirect
    --expect-status <int>              set expected HTTP status code
    --validation-string <string>       set validation-string
```
### Options for API Script Tests
```
    --file,-f <file-name>              json payload
    --script-file <file-name>          specify a script file to update APIScript or BrowserScript
    --bundle <bundle>                  set bundle content
    --entry-file <string>              entry file of a bundle test
```
### Options for Browserscript test
```
    --file,-f <file-name>              json payload
    --script-file <file-name>          specify a script file to update APIScript or BrowserScript
    --bundle <bundle>                  set bundle content
    --entry-file <string>              entry file of a bundle test
    --record-video <boolean>           enable/disable record video, false by default
```
### Options for SSLCertificate test
```             
    --hostname  <host>                 set hostname for ssl test
    --port <int>                       set port 
    --remaining-days-check <int>       set days remaining before expiration of SSL certificate
```
## Examples
### Common Example for All Tests
```
# Update a Synthetic test with multiple options.
synctl update test <synthetic-id> \
    --frequency 5 \
    --label "simple-ping" \
    --location <id1> <id2> ... \
    --retry-interval 3 \
    --url https://www.ibm.com \
    --follow-redirect true \
    --validation-string "a synthetic test" \
    --expect-status 200 \
    --custom-property "key1=value1,key2=value2"
```
### Example for API Script Tests
```
#  Update a test with json payload.
1. Get synthetic configuration and save to test.json
    synctl get test <synthetic-id> --show-json > test.json

2. edit json file and update test.
    synctl update test <synthetic-id> --file/-f test.json

```
### Example for SSLCertificate Tests
```
synctl update test <synthetic-id> \
    --hostname www.ibm.com \
    --remaining-days-check 120
