# Patch Synthetic Test
The command `patch` can be used to updates selected attributes of a Synthetic test, only one attribute can be patched each time.

## Syntax
```
synctl patch test id [options]
```

## Options
```
-h, --help                         show this help message and exit

--active <boolean>                 set active
--frequency <int>                  set frequency
--location <id> [<id> ...]         set location
--description <string>             set description
--label <string>                   set label
--retries <int>                    set retries, min is 0 and max is 2
--retry-interval <int>             set retry-interval, min is 1, max is 10
--operation <method>               HTTP request methods, GET, POST, HEAD, PUT, etc.
--mark-synthetic-call <boolean>    set markSyntheticCall
--timeout <num>ms|s|m              set timeout, accept <number>(ms|s|m)
--script-file <file-name>          specify a script file to update APIScript or BrowserScript
--url <url>                        HTTP URL
--follow-redirect <boolean>        set follow-redirect
--expect-status <int>              set expected HTTP status code
--validation-string <string>       set validation-string
--bundle <bundle>                  set bundle content
--entry-file <string>              entry file of a bundle test
--browser <string>                 browser type, support chrome and firefox
--record-video <boolean>           enable/disable record video, false by default          
--custom-property <key>=<value>    set custom property, should be <key,value> pair

--use-env, -e <name>               use a config hostname
--host <host>                      set hostname
--token <token>                    set token
```

## Examples
Patch test label to simple-ping.
```
synctl patch test <synthetic-id> --label simple-ping
```

set url to `https://www.ibm.com`
```
synctl patch test <synthetic-id> --url https://www.ibm.com
```

Set frequency to 5.
```
synctl patch test <synthetic-id> --frequency 5
```

Set test description to "This is a synthetic test".
```
synctl patch test <synthetic-id> --description "This is a synthetic test"
```

set location new id1, id2...
```
synctl patch test <synthetic-id> --lo <id1> <id2> ...
```

Set retries to 2.
```
synctl patch test <synthetic-id> --retries 2
```

Set retry interval to 5.
```
synctl patch test <synthetic-id> --retry-interval 5
```

Set mark synthetic call to True.
```
synctl patch test <synthetic-id> --mark-synthetic-call True
```

Set timeout to 120s.
```
synctl patch test <synthetic-id> --timeout 120s
```

Disable synthetic test.
```
synctl patch test <synthetic-id> --active false
```

Set HTTP operation to POST.
```
synctl patch test <synthetic-id> --operation POST
```

Update synthetic script.
```
# update synthetic test with new script
synctl patch test <synthetic-id> --script-file new-api-script.js
```

Set followredirect to `true`.
```
synctl patch test <synthetic-id> --follow-redirect true
```

Set expect status to 200.
```
synctl patch test <synthetic-id> --expect-status 200
```

Set validationString to `synthetic-test`
```
synctl patch test <synthetic-id> --validation-string "synthetic-test"
```

Update bundle test with a zip file.
```
synctl patch test <synthetic-id> --bundle synthetic.zip
```

Update bundle test using base64 string.
```
PATCH_BASE64_STR=`cat bundle.zip|base64`
synctl patch test <synthetic-id> --bundle "${PATCH_BASE64_STR}"
```

Set entry file of bundle test.
```
synctl patch test <synthetic-id> --entry-file bundle-test/index.js
```

Set custom properties of a test
```
synctl patch test <synthetic-id> --custom-property key=value
```

Set record video true
```
synctl patch test <synthetic-id> --record-video true
```

Set browser to firefox
```
synctl patch test <synthetic-id> --browser firefox
```

Set multiple custom properties of a test
```
synctl patch test <synthetic-id> --custom-property "key1=value1,key2=value2,key3=value3"
```
