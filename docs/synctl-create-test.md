# synctl create test

Create Synthetic test.

## Syntax
```
synctl create test [options]
```

## Options
```
    -h, --help                          show this help message and exit

    -t <int>, --type <int>              Synthetic type: 0 API Simple, 1 API Script, 2 Browser Script, 3 Webpage Script, 4 Webpage Simple, 5 SSLCertificate
    --location id [id ...]              location id, support multiple locations id
    --label <string>                    friendly name of the Synthetic test
    --description, -d <string>          the description of Synthetic test
    --frequency <int>                   the range is from 1 to 120 minute, default is 15
    --app-id, --application-id <id>     application id
    --url <url>                         HTTP request URL
    --operation <method>                HTTP request methods, GET, POST, HEAD, PUT, etc
    --headers <json>                    HTTP headers
    --body <string>                     HTTP body
    -f, --from-file <file>              Synthetic script, support js file, e.g, script.js
    --bundle <bundle>                   Synthetic bundle test script, support zip file, zip file encoded with base64
    --script-file <file-name>           Synthetic bundle test entry file, e.g, myscript.js
    --retries <int>                     retry times, value is from [0, 2]
    --retry-interval <int>              retry interval, range is [1, 10]
    --follow-redirect <boolean>         to allow redirect, true by default
    --timeout <num>ms|s|m               set timeout, accept <number>(ms|s|m)
    --expect-status <int>               expected status code, Synthetic test will fail if response status is not equal to it, default 200
    --expect-json <string>              An optional object to be used to check against the test response object
    --expect-match <string>             An optional regular expression string to be used to check the test response
    --expect-exists <string>            An optional list of property labels used to check if they are present in the test response object
    --expect-not-empty <string>         An optional list of property labels used to check if they are present in the test response object with a non-empty value
    --allow-insecure <boolean>          if set to true then allow insecure certificates
    --custom-properties <string>        An object with name/value pairs to provide additional information of the Synthetic test
    --browser <string>                  browser type, support chrome and firefox
    --record-video <boolean>            set true to record video
    --from-json <json>                  full Synthetic test payload, support json file
    --hostname <host>                   set hostname for ssl test
    --port <int>                        set port, default is 443 
    --remaining-days-check <int>        set remaining days before expiration of SSL certificate

    --use-env <name>, -e <name>         use a specified configuration
    --host <host>                       set hostname
    --token <token>                     set token
```

## Examples  

### Create API Simple test  

Create API Simple test, test frequency is 5min. Use command `synctl get lo` to get location id.
```
synctl create test -t 0 \
    --label "simple-ping" \
    --url "https://httpbin.org/get" \
    --location "$LOCATION" \
    --frequency 5
```

Create API Simple test and specify multiple location id.
```
synctl create test -t 0 \
    --label "simple-ping" \
    --url "https://httpbin.org/get" \
    --location "$LOCATION1" "$LOCATION2" "$LOCATION3" ...
```
Create API Simple test and specify application id, retry, headers, and timeout.
```
synctl create test -t 0 \
    --label "API-simple-test" \
    --description "this is a test example" \
    --url <url> \
    --location "$LOCATION" \
    --frequency 5 \
    --app-id "$APPID" \
    --operation GET \
    --headers '{"content-type":"application/json"}' \
    --retries 2 \
    --retry-interval 2 \
    --follow-redirect true \
    --timeout 1m \
    --allow-insecure true
```

Expect Status example.
```
synctl create test -t 0 \
    --label "ping-expect-status-200" \
    --url "https://httpbin.org/get" \
    --location "$LOCATION1" \
    --expect-status 200
```

Expect Json example.
```
synctl create test -t 0 \
    --label "ping-expect-json" \
    --url "https://httpbin.org/json" \
    --location "$LOCATION1" \
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

Expect Match example
```
synctl create test -t 0 \
    --label expect-match-test \
    --url https://www.ibm.com \
    --lo "$LOCATION1" \
    --expect-match ibm
```


Expect esists example
```
synctl create test -t 0 \
    --label expect-exists-test \
    --url https://httpbin.org/json \
    --location "$LOCATION1" \
    --expect-exists '["slideshow"]'
```

Expect not empty example
```
synctl create test -t 0 \
    --label expect-not-empty-test \
    --url https://httpbin.org/json \
    --location "$LOCATION1" \
    --expect-not-empty '["slideshow"]'

```

### Create API Script test Examples

Create a simple API script from file.
```
synctl create test -t 1 \
    --label "simple-api-script" \
    --from-file http-scripts/http-get.js \
    --location "$LOCATION" \
    --frequency 5
```

Custom properties example
```
synctl create test -t 1 \
    --label custom-properties-test \
    --from-file api-script.js \
    --location "$LOCATION1" \
    --custom-properties '{"key1":"value1"}'
```

Create bundle test with a zip file
```
synctl create test -t 1 --label syn-bundle-zip-test \
    --bundle synthetic.zip \
    --script-file index.js \
    --location "$LOCATION" \
    --frequency 5
```

Create bundle test from base64 string
```
BASE64STR=`cat synthetic.zip|base64`

synctl create test -t 1 --label "syn-bundle-test" \
    --bundle "${BASE64STR}" \
    --script-file index.js  \
    --location "$LOCATION"  \
    --frequency 5
```

Create bundle test
```
synctl create test -t 1 --label "syn-bundle-test" \
    --bundle "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" \
    --script-file index.js \
    --location "$LOCATION" \
    --frequency 5
```

### Create Browser Script test examples

create a browser script test
```
synctl create test -t 2 \
    --label browser-script-test \
    --from-file browserscripts/api-sample.js \
    --location "$LOCATION" \
    --frequency 15
```

Create browser bundle test using a zip file
```
synctl create test -t 2 \
    --label browser-script-test-zip \
    --bundle browserscript-bundle.zip \
    --script-file mytest.js \
    --location "$LOCATION" \
    --frequency 15
```

Create browser bundle test using base64 string
```
synctl create test -t 2 \
    --label "browser-script-test-bundle" \
    --location "$LOCATION" \
    --frequency 15 \
    --browser firefox \
    --script-file mytest.js \
    --bundle "UEsDBAoAAAAAAHltFlUAAAAAAAAAAAAAAAAEABwAbGliL1VUCQADlRcDY2izBGN1eAsAAQToAwAABOgDAABQSwMEFAAIAAgA1FkYVQAAAAAAAAAAVAMAAA8AHABsaWIvbXlzY3JpcHQuanNVVAkAA6CXBWOglwVjdXgLAAEE6AMAAAToAwAAlVPBbuIwEL3zFSOLQ5C65t5qVwIpB9RuVbW5R8YMidVgp56hWYT67zsOoUuLkFifEue9N2/eTGzwxLAHQ4SR4QN+QsS3rYuYKVsbpyZ3I0M7b2G99ZZd8MBIPHe+yiawH41AznQK3ry7yjACB+i6Ti8FoG3Y9N+tFAkN6iZUmfp1ftQNqJm1SASJB62pMBVOXNMZxzBextCJQ10hZ6pmbm+n09M6CX700mJch7gBQhNtDaa3/R9GEpwgrAeBC07GmdK0LFOl8u0C5lCasokm9Kt73FGmJEyukZ1VJ7fjVXTvQpAXnT8W+fNED11kJ40NQ0rxADtuEJY7kESK9CzjMK3roQ0eQP29TPQ8w4ExmO5ltYzdNCf+4Ae8HAK4+ac2UK4J8unT5i18kzg2xOYVgWxE9FQHvlq6EN7LJ+1C+PwFdGx2vGXXaOfJVTWTTED2qVg8lcXzYp6Xj7Pfefkwm+cPqQyFDXItG9Zv18fdaBNWW7GGf9oQmSTZfa95/CMSRM5fUEsHCJkl42ODAQAAVAMAAFBLAwQUAAgACAB5bRZVAAAAAAAAAAARAQAACQAcAG15dGVzdC5qc1VUCQADlRcDYxC7BGN1eAsAAQToAwAABOgDAABdjzEOwjAMRfeewooYgoTSHcTCFdjY2mAVozQOiRkK4u6kVEjgzXp+/0u/CSjwBMEiB4oDvGAPGW93ymiNawP17TgVnymJuxaz3jWN51g4oAs8WJM4bc0GVmWKckEh7yqp1p90xqWBOCr556NDQiM+OKJKzPhUsdZD12MoSl6gVo/SZQHhz+p50ne9rfcbUEsHCA5zkg+OAAAAEQEAAFBLAQIeAwoAAAAAAHltFlUAAAAAAAAAAAAAAAAEABgAAAAAAAAAEAD/QQAAAABsaWIvVVQFAAOVFwNjdXgLAAEE6AMAAAToAwAAUEsBAh4DFAAIAAgA1FkYVZkl42ODAQAAVAMAAA8AGAAAAAAAAQAAAP+BPgAAAGxpYi9teXNjcmlwdC5qc1VUBQADoJcFY3V4CwABBOgDAAAE6AMAAFBLAQIeAxQACAAIAHltFlUOc5IPjgAAABEBAAAJABgAAAAAAAEAAAD/gRoCAABteXRlc3QuanNVVAUAA5UXA2N1eAsAAQToAwAABOgDAABQSwUGAAAAAAMAAwDuAAAA+wIAAAAA" 
```

#### Create Webpage Script test

```
synctl create test -t 3 \
    --label "webpage-script-test" \
    --location "$LOCATION" --frequency 15 \
    --from-file side/webpage-script.side  \
    --browser chrome
```

#### Create Webpage Action test
```
synctl create test -t 4 \
    --label "browser-test-webpageaction" \
    --url "https://httpbin.org/get" \
    --location "$LOCATION" --frequency 5 \
    --record-video true \
    --browser chrome
```

#### Create SSLCertificate test
```
synctl create test -t 5 \
    --label "ssl-certificate-test" \
    --hostname "httpbin.org" \
    --port 443 \
    --remaining-days-check 30 \
    --lo "$LOCATION"  
```

#### Create Synthetic test with json payload  

```
synctl create test -t <type> --from-json payload/api-script.json
```


**Note:** Support specify application id when create synthetic test, get an application id through command `synctl get app`.


