# synctl patch test
The command `patch` can be used to updates selected attributes of a Synthetic test, only one attribute can be patched each time.

## Syntax
```
synctl patch test [id] [options]
```

## Options

### Common options
```
    -h, --help                         show this help message and exit
    --verify-tls                       verify tls certificate

    --filter <key>=<value>             pause/unpause tests in bulk by locationid or applicationid;
                                       only supported together with --active; use instead of [id]
                                       supported keys: locationid, applicationid
    --active <boolean>                 pause (false) or unpause (true) the test; required when --filter is used
    --frequency <int>                  set frequency
    --location <id> [<id> ...]         set location
    --description <string>             set description
    --label <string>                   set label
    --retries <int>                    set retries, min is 0 and max is 2
    --retry-interval <int>             set retry-interval, min is 1, max is 10
    --timeout <num>ms|s|m              set timeout, accept <number>(ms|s|m)
    --custom-properties <key>=<value>  set custom property, should be <key,value> pair
    
    --use-env, -e <name>               use a config hostname
    --host <host>                      set hostname
    --token <token>                    set token
```

### Options for API Simple test
```
    --url <url>                        HTTP URL
    --follow-redirect <boolean>        set follow-redirect
    --mark-synthetic-call <boolean>    set markSyntheticCall
    --expect-status <int>              set expected HTTP status code
    --operation <method>               HTTP request methods, GET, POST, HEAD, PUT, etc.
    --validation-string <string>       set validation-string
    --expect-status <int>              expected status code, Synthetic test will fail if response status is not equal to it, default 200
    --expect-json <string>             An optional object to be used to check against the test response object
    --expect-match <string>            An optional regular expression string to be used to check the test response
    --expect-exists <string>           An optional list of property labels used to check if they are present in the test response object
    --expect-not-empty <string>        An optional list of property labels used to check if they are present in the test response object with a non-empty value
    --allow-insecure <boolean>         if set to true then allow insecure certificates
```

### Options for API script test
```
    --script <file>                    load script (.js) from file
    --bundle <bundle>                  Synthetic bundle test script, support zip file (.zip) path or zip file content encoded with base64
    --bundle-entry-file <file-name>    Synthetic bundle test entry file, e.g, myscript.js
    --mark-synthetic-call <boolean>    set markSyntheticCall
```

### Options for Browser Script test
```
    --script <file>                    load script (.js) from file
    --bundle <bundle>                  Synthetic bundle test script, support zip file (.zip) path or zip file content encoded with base64
    --bundle-entry-file <file-name>    Synthetic bundle test entry file, e.g, myscript.js
    --browser <string>                 browser type, support chrome and firefox
    --record-video <boolean>           enable/disable record video, false by default
    --mark-synthetic-call <boolean>    set markSyntheticCall
```

### Options for Webpage Simple test
```
    --url <url>                        HTTP URL
    --mark-synthetic-call <boolean>    set markSyntheticCall
    --record-video <boolean>           enable/disable record video, false by default
    --browser <string>                 browser type, support chrome and firefox
    --mark-synthetic-call <boolean>    set markSyntheticCall
```

### Options for Webpage Script test
```
    --script <file>                    load script (.side) from file
    --mark-synthetic-call <boolean>    set markSyntheticCall
    --record-video <boolean>           enable/disable record video, false by default
    --browser <string>                 browser type, support chrome and firefox
    --mark-synthetic-call <boolean>    set markSyntheticCall
```

### Options for SSLCertificate test
```
    --hostname <host>                  set hostname for ssl test
    --port <int>                       set port 
    --remaining-days-check <int>       set days remaining before expiration of SSL certificate
```

### Options for DNS test
```
    --cname <boolean>                   enable the canonical name in the DNS response, false by default
    --lookup <host>                     set the name or IP address of the host
    --lookup-server-name <boolean>      enable recursive DNS lookups, false by default
    --port <int>                        set port, default is 53
    --query-time <string>               an object with name/value pairs used to validate the test response time
    --query-type <string>               DNS query type: Value must be one of ALL, ALL_CONDITIONS, ANY, A, AAAA, CNAME, NS. Default value is A.
    --recursive-lookups <boolean>       enables recursive DNS lookups, false by default
    --server <string>                   set IP address of the DNS server
    --server-retries <int>              set number of times to try a timed-out DNS lookup before returning failure. Default is 1
    --target-values <str>               set list of filters to be used to validate the test response
    --transport <str>                   set protocol used to do DNS check. Only UDP is supported.
```

### Options for ICMP test
```
    --target-host <string>              set the target host for ICMP ping test
    --packet-count <int>                set number of packets to send
    --packet-size <int>                 set packet size in bytes
    --packet-timeout <string>           set per-packet timeout 
    --use-ipv6 <boolean>                use IPv6 instead of IPv4
    --use-dns <boolean>                 enable DNS resolution
    --validation-rules <string>         set list of validation rules for ICMP test response
```


## Examples
### Common Examples for All tests

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

# Pause a single Synthetic test
synctl patch test <synthetic-id> --active false

# Pause all tests running on a given location
synctl patch test --filter=locationid=<locationId> --active false

# Re-enable all tests on a given location
synctl patch test --filter=locationid=<locationId> --active true

# Pause all tests associated with a given application
synctl patch test --filter=applicationid=<applicationId> --active false

# Set custom properties of a test
synctl patch test <synthetic-id> --custom-properties key=value

# Set multiple custom properties of a test
synctl patch test <synthetic-id> --custom-properties "key1=value1,key2=value2,key3=value3"
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
synctl patch test <synthetic-id> --script new-api-script.js

# Update bundle test with a zip file
synctl patch test <synthetic-id> --bundle synthetic.zip

# Update bundle test using base64 string
PATCH_BASE64_STR=`cat bundle.zip|base64`
synctl patch test <synthetic-id> --bundle "${PATCH_BASE64_STR}"

# Set entry file of bundle test
synctl patch test <synthetic-id> --bundle-entry-file bundle-test/index.js
```

### Examples for Browser Script tests
```
# Set browser to firefox
synctl patch test <synthetic-id> --browser firefox

# Set multiple custom properties of a test
synctl patch test <synthetic-id> --custom-properties "key1=value1,key2=value2,key3=value3"
```

### Examples for Webpage Simple tests
```
# Set URL of Webpage Simple to `https://www.ibm.com`
synctl patch test <synthetic-id> --url https://www.ibm.com

# Set browser to firefox
synctl patch test <synthetic-id> --browser firefox
```

### Examples for Webpage Script tests
```
# Update synthetic test with new script
synctl patch test <synthetic-id> --script seleniumide-script.side

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

```
### Examples for DNS test
```
# Set lookup of a DNS test
synctl patch test <synthetic-id> --lookup true

# Set port of DNS test
synctl patch <synthetic-id> --port 53

# Set query type of DNS test
synctl patch test <synthetic-id> --query-type A

# Set server of DNS test
synctl patch test <synthetic-id> --server 8.8.8.8

# Set quesry time of DNS test
synctl patch test <synthetic-id> --query-time  '{"key": "responseTime", "operator": "LESS_THAN", "value": 120}'
```

### Examples for ICMP test
```
# Set target host of an ICMP test
synctl patch test <synthetic-id> --target-host 8.8.8.8

# Set packet count of ICMP test
synctl patch test <synthetic-id> --packet-count 10

# Set packet size of ICMP test
synctl patch test <synthetic-id> --packet-size 128

# Set packet timeout of ICMP test
synctl patch test <synthetic-id> --packet-timeout "5s"

# Enable IPv6 for ICMP test
synctl patch test <synthetic-id> --use-ipv6 true

# Disable DNS resolution for ICMP test
synctl patch test <synthetic-id> --use-dns false

# Set validation rules of ICMP test
synctl patch test <synthetic-id> --validation-rules '[{"key": "packetLoss", "operator": "LESS_THAN", "value": 10}]'
```
