# Synthetic CLI Command
Synthetic Command Line Tool(synctl) is used to manage synthetic tests, locations and credentials.

# Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Upgrade](#upgrade)
- [Size the PoP hardware configuration](#size-the-pop-hardware-configuration)
- [Estimate the cost of Instana-hosted PoP](#estimate-the-cost-of-instana-hosted-pop)
- [Configure an Instana Backend](#configure-an-instana-backend)
    - [Use a configuration file](#use-a-configuration-file-recommended)
    - [Use command options](#use-command-options)
    - [Use environment variables](#use-environment-variables)
- [Manage configuration files](#manage-configuration-files)
    - [synctl config Syntax](#synctl-config-syntax)
    - [synctl config Options](#synctl-config-options)
    - [synctl config Examples](#synctl-config-examples)
- [Query Synthetic Test](#query-synthetic-test)
    - [synctl get test Syntax](#synctl-get-test-syntax)
    - [synctl get test Options](#synctl-get-test-options)
    - [synctl get test Examples](#synctl-get-test-examples)
- [Create Synthetic test](#create-synthetic-test)
    - [synctl create test Syntax](#synctl-create-test-syntax)
    - [synctl create test Options](#synctl-create-test-options)
    - [synctl create test Examples](#synctl-create-test-examples)
        - [Create API Simple test](#create-api-simple-test)
        - [Create API Script test](#create-api-script-test)
        - [Create Browser Script test](#create-browser-script-test)
        - [Create Webpage Script test](#create-webpage-script-test)
        - [Create Webpage Action test](#create-webpage-action-test)
        - [Create Synthetic test with json payload](#create-synthetic-test-with-json-payload)
- [Patch Synthetic Test](#patch-synthetic-test)
    - [synctl patch Syntax](#synctl-patch-syntax)
    - [synctl patch Options](#synctl-patch-options)
    - [synctl patch Examples](#synctl-patch-examples)
- [Update Synthetic Test](#update-synthetic-test)
    - [synctl update Syntax](#synctl-update-syntax)
    - [synctl update Options](#synctl-update-options)
    - [synctl update Examples](#synctl-update-examples)
- [Delete Synthetic test](#delete-synthetic-test)
    - [synctl delete test Syntax](#synctl-delete-test-syntax)
    - [synctl delete test Options](#synctl-delete-test-options)
    - [synctl delete test Examples](#synctl-delete-test-examples)
- [Manage Synthetic Locations](#manage-synthetic-locations)
    - [Manage Location Syntax](#manage-location-syntax)
    - [Query Synthetic location](#query-synthetic-location)
    - [Delete Synthetic location](#delete-synthetic-location)
- [Manage Credentials](#manage-credentials)
    - [Display all credentials](#display-all-credentials)
    - [Create a credential](#create-a-credential)
    - [Update a credential](#update-a-credential)
    - [Delete a credential](#delete-a-credential)
- [Manage Application](#manage-application)
    - [Get application Syntax](#get-application-syntax)
    - [Get application Examples](#get-application-examples)
- [Query Smart Alerts](#query-smart-alerts)
    - [synctl get alert Syntax](#synctl-get-alert-syntax)
    - [synctl get alert Options](#synctl-get-alert-options)
    - [synctl get alert Examples](#synctl-get-alert-examples)
- [Create Smart alert](#create-smart-alert)
    - [synctl create alert Syntax](#synctl-create-alert-syntax)
    - [synctl create alert Options](#synctl-create-alert-options)
    - [synctl create alert Examples](#synctl-create-alert-examples)
- [Update a Smart Alert](#update-a-smart-alert)
    - [synctl update alert Syntax](#synctl-update-alert-syntax)
    - [synctl update alert Options](#synctl-update-alert-options)
    - [synctl update Examples](#synctl-update-examples)
- [Delete a Smart alert](#delete-a-smart-alert)
    - [synctl delete alert Syntax](#synctl-delete-alert-syntax)
    - [synctl delete alert Examples](#synctl-delete-alert-examples)
  
# Features
- CRUD of Synthetic test, support API Simple, API Script, Browser Script, etc.
- Query/delete of Synthetic location.
- Query/create/update/delete of Synthetic credential.
- Support multiple configurations of backend server.
- CRUD of Smart alerts.

# Prerequisites
- [Python 3.6+](https://www.python.org/downloads/)
- [requests 2.27+](https://requests.readthedocs.io/en/latest/)

# Installation
If you have installed synctl(version 1.0.x) before, make sure remove it via `rm /usr/local/bin/synctl`. 
```
pip3 install synctl
```

**Note:** To install python3 on Windows, see [Python](https://www.python.org/downloads/windows/).

# Upgrade
Upgrade `synctl` to latest version.
```
pip3 install --upgrade synctl
```

Upgrade `synctl` to a specified version.
```
pip3 install --upgrade synctl==<version>
```

# Size the PoP hardware configuration
synctl can be used to estimate the size of the PoP hardware configuration.

### synctl pop-sizing Syntax
```
# synctl get pop-size

# synctl get size
```
# Estimate the cost of Instana-hosted PoP
synctl can be used to estimate the cost of Instana-hosted synthetic PoP.

### synctl cost estimation Syntax
```
# synctl get pop-cost

# synctl get cost
```
# Configure an Instana Backend
`synctl` support three types of configurations:
- Use configurations file, the default config file is under `~/.synthetic/config.json`.
- Use `--host` and `--token` options to specify the host and token.
- Set environment variables before run synctl command, `SYN_SERVER_HOSTNAME`, `SYN_API_TOKEN` are used to store host and token.

**Note:** The priority of configuration is command options > environment variables > config file.

### Create a token
1. Log in to the Instana UI. 
2. Navigate to the `Settings` page, go to the `API Tokens` tab under Team Settings.
3. Click on `New API Token` in the upper right corner to create a new token with proper permissions.

### Use a configuration file (Recommended)
The configuration file is stored under `~/.synthetic/config.json` by default, uses can edit it directly or use `synctl config` command to manage configuration information. Below is an example to configure a backend server:
```
# set your backend host and token, and give it an alias name, and set it as default
synctl config set \
    --host "https://test-instana.pink.instana.rocks" \
    --token "Your Token" \
    --name "pink" \
    --default

# list configurations
synctl config list
```
**Note:** By default, config file is `~/.synthetic/config.json`.

### Use command options
Synthetic `synctl` command can accept `--host <host>` and `--token <token>` option to specify host and token if there is not a configuration file. See below examples:

```
# retrieve all tests with --host and --token
synctl get test --host "https://test-instana.pink.instana.rocks" --token <Your-Token>

# get all locations with host and token
synctl get location --host "https://test-instana.pink.instana.rocks" --token <Your-Token>
```

### Use environment variables

```
# set SYN_SERVER_HOSTNAME and SYN_API_TOKEN
export SYN_SERVER_HOSTNAME="https://test-instana.pink.instana.rocks"
export SYN_API_TOKEN="Your Token"

# then run command with no options
# retrieve all tests
synctl get test

# retrieve all location
synctl get location
```

# Manage configuration files
`synctl config` can be used to manage configuration files.  

### synctl config Syntax
```
synctl config {set,list,use,remove} [options]

# commands
set        configure a new backend server
list       list all configurations
use        modify a configuration
remove     delete a configuration
```

### synctl config Options
```
-h, --help            show this help message and exit
--host <host>         set hostname
--token, -t <token>   set token
--env, --name <name>  specify which config to use
--default             set as default
```

### synctl config Examples

```
# configure a backend, name it as pink and set it as default
synctl config set \
    --host "https://test-instana.pink.instana.rocks" \
    --token "Your Token" \
    --name "pink" \
    --default

# set pink as default
synctl config use --name pink --default

# remove a config
synctl config remove --name pink
```

# Query Synthetic Test
`synctl get test` can be used to query Synthetic tests. In the command options, we use number [0, 4] to represent different Synthetic type for simple. They are API Simple(0), API Script(1), Browser Script(2), Webpage Script(3), Webpage Simple(4).

### synctl get test Syntax
```
synctl get test [id] [options]
```

### synctl get test Options
```
-h, --help             show this help message and exit

--type, -t <int>       Synthetic type, 0 API Simple, 1 Api Script, 2 Browser Script, 3 Webpage Script, 4 Webpage Simple
--window-size <window> set synthetic result window size, support [1,60]m, [1-24]h
--save-script          save script to local, default is test label
--show-script          output test script to terminal
--show-details         output test or location details to terminal
--show-json            output test json to terminal
--show-result          show test latency and success rate
--filter               filter tests based on locationId/applicationId

--use-env, -e <name>   use a specified config
--host <host>          set hostname
--token <token>        set token
```

### synctl get test Examples
```
# Display all tests
synctl get test

# filter test by synthetic type
# API Simple(0), Api Script(1), Browser Script(2) and Webpage Script(3),  Webpage Simple(4) are supported
# type is number of [0, 4]
synctl get test -t <type>

# get API Simple test, and specify its type 0
synctl get test -t 0


# get synthetic test result with --window-size, support [1, 60]m, [1-24]h
synctl get test --window-size 30m

synctl get test --window-size 6h

# show test details
synctl get test <id> --show-details

# save test script to a local file, file name is test label
synctl get test <id> --save-script

# show test script
synctl get test <id> --show-script

# show a test payload in json
synctl get test <id> --show-json

# filter tests based on locationId
synctl get test --filter=locationid=<locationId>

# filer tests based on applicationId
synctl get test --filter=applicationid=<applicationId>
```

# Create Synthetic test
`synctl create test` is used to create Synthetic test.

### synctl create test Syntax
```
synctl create test [options]
```
### synctl create test Options
```
-h, --help                          show this help message and exit

-t <int>, --type <int>              Synthetic type: 0 API Simple, 1 API Script, 2 Browser Script, 3 Webpage Script, 4 Webpage Simple
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

--use-env <name>, -e <name>         use a specified configuration
--host <host>                       set hostname
--token <token>                     set token
```

### synctl create test Examples  

#### Create API Simple test  

```
# get location id
synctl get location
synctl create test -t 0 \
    --label "simple-ping" \
    --url "https://httpbin.org/get" \
    --location "$LOCATION" \
    --frequency 5

# or schedule multiple locations
synctl create test -t 0 \
    --label "simple-ping" \
    --url "https://httpbin.org/get" \
    --location "$LOCATION1" "$LOCATION2" "$LOCATION3" ...

# API Simple example
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

# expectStatus example
synctl create test -t 0 \
    --label "ping-expect-status-200" \
    --url "https://httpbin.org/get" \
    --location "$LOCATION1" \
    --expect-status 200

# expectJson example
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

# expectMatch example
synctl create test -t 0 \
    --label expect-match-test \
    --url https://www.ibm.com \
    --lo "$LOCATION1" \
    --expect-match ibm

# expectExists example
synctl create test -t 0 \
    --label expect-exists-test \
    --url https://httpbin.org/json \
    --location "$LOCATION1" \
    --expect-exists '["slideshow"]'

# expectNotEmpty example
synctl create test -t 0 \
    --label expect-not-empty-test \
    --url https://httpbin.org/json \
    --location "$LOCATION1" \
    --expect-not-empty '["slideshow"]'

```

#### Create API Script test  

```
# a simple API script
synctl create test -t 1 \
    --label "simple-api-script" \
    --from-file http-scripts/http-get.js \
    --location "$LOCATION" \
    --frequency 5

# custom properties example
synctl create test -t 1 \
    --label custom-properties-test \
    --from-file api-script.js \
    --location "$LOCATION1" \
    --custom-properties '{"key1":"value1"}'

# create bundle test with a zip file
synctl create test -t 1 --label syn-bundle-zip-test \
    --bundle synthetic.zip \
    --script-file index.js \
    --location "$LOCATION" \
    --frequency 5

# create bundle test 1
BASE64STR=`cat synthetic.zip|base64`

synctl create test -t 1 --label "syn-bundle-test" \
    --bundle "${BASE64STR}" \
    --script-file index.js  \
    --location "$LOCATION"  \
    --frequency 5

# or create bundle test 2
synctl create test -t 1 --label "syn-bundle-test" \
    --bundle "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" \
    --script-file index.js \
    --location "$LOCATION" \
    --frequency 5
```

#### Create Browser Script test


```
# create a browser script test
synctl create test -t 2 \
    --label browser-script-test \
    --from-file browserscripts/api-sample.js \
    --location "$LOCATION" \
    --frequency 15


# create browser bundle test using a zip file
synctl create test -t 2 \
    --label browser-script-test-zip \
    --bundle browserscript-bundle.zip \
    --script-file mytest.js \
    --location "$LOCATION" \
    --frequency 15

# create browser bundle test using base64 string
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

#### Create Synthetic test with json payload  

```
synctl create test -t <type> --from-json payload/api-script.json
```


**Note:** Support specify application id when create synthetic test, get an application id through command `synctl get app`.



# Patch Synthetic Test
The command `patch` can be used to updates selected attributes of a Synthetic test, only one attribute can be patched each time.

### synctl patch Syntax
```
synctl patch test id [options]
```

### synctl patch Options
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

### synctl patch Examples

```
# set label to simple-ping
synctl patch test <synthetic-id> --label simple-ping

# set url to https://www.ibm.com
synctl patch test <synthetic-id> --url https://www.ibm.com

# set frequency to 5
synctl patch test <synthetic-id> --frequency 5

# set description to "This is a synthetic test"
synctl patch test <synthetic-id> --description "This is a synthetic test"

# set location new id1
synctl patch test <synthetic-id> --lo <id1> <id2> ...

# set retries to 2
synctl patch test <synthetic-id> --retries 2

# set retry-interval to 5
synctl patch test <synthetic-id> --retry-interval 5

# set mark-synthetic-call to True
synctl patch test <synthetic-id> --mark-synthetic-call True
 
# set timeout to 120s
synctl patch test <synthetic-id> --timeout 120s

# disable synthetic test
synctl patch test <synthetic-id> --active false

# set operation to POST
synctl patch test <synthetic-id> --operation POST

# update synthetic script
# save script to local, script name is <label>.js 
synctl get test <synthetic-id> --save-script

# update synthetic test with new script
synctl patch test <synthetic-id> --script-file new-api-script.js

# set followredirect to true
synctl patch test <synthetic-id> --follow-redirect true

# set expectStatus to 200
synctl patch test <synthetic-id> --expect-status 200

# set validationString to synthetic-test
synctl patch test <synthetic-id> --validation-string "synthetic-test"

# update bundle test with a zip file
synctl patch test <synthetic-id> --bundle synthetic.zip

# update bundle test using base64 string
PATCH_BASE64_STR=`cat bundle.zip|base64`
synctl patch test <synthetic-id> --bundle "${PATCH_BASE64_STR}"

# set entry file of bundle test
synctl patch test <synthetic-id> --entry-file bundle-test/index.js

# set custom properties of a test
synctl patch test <synthetic-id> --custom-property key=value

#set record video true
synctl patch test <synthetic-id> --record-video true

#set browser to firefox
synctl patch test <synthetic-id> --browser firefox

# set multiple custom properties of a test
synctl patch test <synthetic-id> --custom-property "key1=value1,key2=value2,key3=value3"
```

# Update Synthetic Test

### synctl update Syntax
```
synctl update test <id> [options]
```

### synctl update Options
```
-h, --help            show this help message and exit

--file,-f <file-name> json payload

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
--record-video <boolean>           enable/disable record video, false by default          
--custom-property <key>=<value>    set custom property, should be <key,value> pair

--use-env, -e <name>  use a config hostname
--host <host>         set hostname
--token <token>       set token
```

### synctl update Examples
```
# get synthetic configuration and save to test.json
synctl get test <synthetic-id> --show-json > test.json

# edit json file and update
synctl update test <synthetic-id> --file/-f test.json

# update a synthetic test with multiple options
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

# Delete synthetic test

### synctl delete test Syntax
```
synctl delete {location,lo,test,cred} [id...] [options]
```

### synctl delete test Options
``` 
-h, --help            show this help message and exit

--match-regex <regex> use a regex to match synthetic label
--match-location <id> delete tests match this location id
--no-locations        delete tests with no locations

--use-env, -e <name>  specify a config name
--host <host>         set hostname
--token <token>       set token
```

### synctl delete test Examples
```
# delete a synthetic test
synctl delete test <synthetic-id>

# delete several synthetic tests
synctl delete test <synthetic-id-1> <synthetic-id-2> <synthetic-id-3> ...


# delete test with --match-regex, support regex, for regex refer
# Regular expression operations https://docs.python.org/3/library/re.html
# delete all tests which label match regex "^ping-test-*"
synctl delete test --match-regex "^ping-test-*"

# delete all tests
synctl delete test --match-regex ".*"

# delete all tests with <location-id>
# it will not delete tests with multiple locations
# For example, `synctl delete test --match-location A` will not delete test with location [A, B]
synctl delete test --match-location <location-id>

# delete all tests which has no locations
synctl delete test --no-locations
```

# Manage Synthetic Locations

### Manage Location Syntax
```
# get location
synctl get {location,lo} [id] [options]

Options:
--show-details        show location details

# delete location
synctl delete {location, lo} [id...]
```

### Query Synthetic location

```
# Display Synthetic Location
synctl get location

# Display synthetic location details
synctl get location <location-id> --show-details
```

### Delete Synthetic location

```
# delete a synthetic location
synctl delete location <location-id>

# delete several synthetic location
synctl delete location <location-id-1> <location-id-2> <location-id-3> ...
```

# Manage Credentials

### Display all credentials

```
synctl get cred
```

### Create a credential

```
synctl create cred --key <key-name> --value <value>
```

### Update a credential

```
synctl update cred <cred-name> --value <value>
```

### Delete a credential

```
synctl delete cred <key-name>
```

# Manage Application

### Get application Syntax
```
synctl get {application,app} [id] [options]

Options:
--name-filter <app>   filter application by name, only applicable for application name
```
### Get application Examples

```
# get all application
synctl get app

# filter application by --name-filter, or pattern that application name contains
synctl get app --name-filter "<application-name>"

# then create test with application id
synctl create test -t 0 --app-id <application-id> ...
```
# Query Smart Alerts
`synctl get alert ` can be used to query Smart Alerts. 

### synctl get alert Syntax
```
synctl get alert [id] [options]
```
### synctl get alert Options
```
-h, --help             show this help message and exit
--show-details         output alert details to terminal
--show-json            output alert json to terminal
--use-env, -e <name>   use a specified config
--host <host>          set hostname
--token <token>        set token
```
# Query Test Results
`synctl get result` can be used to query Test Results

### synctl get result Syntax
```
synctl get result [id] [options]
```
### synctl get result Options
```
-h, --help               show this help message and exit
--test                   synthetic-test id
--window-size <window>   set synthetic result window size, support [1,60]m, [1-24]h
--har                    save HAR to local
--use-env, -e <name>     use a specified config
--host <host>            set hostname
--token <token>          set token
```
### synctl get result Examples
```
# Display result list  with --window-size, support [1, 60]m, [1-24]h
synctl get result --test <test-id> --window-size 30m

# show result details with --window-size, support [1, 60]m, [1-24]h
synctl get result <id> --test <test-id> --window-size 6h

# save har to local 
synctl get result <id> --test <test-id> --har
```
# Create Smart alert
`synctl create alert` is used to create Smart Alerts.

### synctl create alert Syntax
```
synctl create alert [options]
```

### synctl create alert Options
```
-h, --help                            show this help message and exit
--test id [id ...]                    synthetic-test id, support multiple synthetic tests id
--name <string>                       friendly name of the Smart Alerts
--description, -d <string>            the description of Smart Alerts
--severity <string>                   the severity of alert is either warning or critical
--alert-channel <id>                  alerting channel
--violation-count <int>               the number of consecutive failures to trigger an alert
--tag-filter-expression <json>        tag filter expression
```
### synctl create alert Examples
```
# get synthetic test
synctl get test 
# get alert channel
synctl get alert-channel

synctl create alert --name "Smart-alert" \
       --alert-channel "$ALERT_CHANNEL" \
       --test "$SYNTHETIC_TEST" \
       --violation-count 2

# or schedule a smart alert for multiple synthetic tests
synctl create alert --name "Smart-alert" \
       --alert-channel "$ALERT_CHANNEL" \
       --test "$SYNTHETIC_TEST1" "$SYNTHETIC_TEST2" "$SYNTHETIC_TEST3" ...  \
       --violation-count 2

# create alert with tagFilterExpression       
synctl create alert --name "smart alert" \
        --test "$SYNTHETIC_TEST1" "$SYNTHETIC_TEST2"... \
        --alert-channel "$ALERT_CHANNEL" \
        --severity critical \
        --violation-count 3 \
        --tag-filter-expression '{"type": "EXPRESSION", "logicalOperator": "AND", "elements": []}'
```
# Update a Smart Alert

### synctl update alert Syntax
```
synctl update alert <id> [options]
```

### synctl update alert Options
```
-h, --help                          show this help message and exit

--file,-f <file-name>               json payload
--test id [id ...]                  synthetic-test id, support multiple synthetic tests id
--name <string>                     friendly name of the Smart Alerts
--description, -d <string>          the description of Smart Alerts
--severity <string>                 the severity of alert is either warning or critical
--alert-channel <id>                alerting channel
--violation-count <int>             the number of consecutive failures to trigger an alert
--tag-filter-expression <json>      tag filter expression
--enable                            enable smart alert
--disable                           disable smart alert

--use-env, -e <name>                use a config hostname
--host <host>                       set hostname
--token <token>                     set token
```

### synctl update Examples
```
# get smart alert configuration and save to alert.json
synctl get alert <alert-id> --show-json > alert.json

# edit json file and update
synctl update alert <alert-id> --file/-f alert.json

# update a smart alert with multiple options
synctl update alert <alert-id> --name "Smart-alert" \
    --alert-channel "$ALERT_CHANNEL1" "$ALERT_CHANNEL2" "$ALERT_CHANNEL3" ... \
    --test "$SYNTHETIC_TEST1" "$SYNTHETIC_TEST2" "$SYNTHETIC_TEST3" ... \
    --violation-count 2 \
    --severity warning

# update a smart alert with tagfilter option
synctl update alert <alert-id> --tag-filter-expression '{"type": "EXPRESSION", "logicalOperator": "AND", "elements": []}'
    
# enable/disable a smart alert
synctl update alert <alert-id> --enable
synctl update alert <alert-id> --disable
```

# Delete a Smart alert
### synctl delete alert Syntax
```
synctl delete alert [id...] 
```
### synctl delete alert Examples
```
# delete a smart test
synctl delete alert <alert-id>

# delete several smart alert
synctl delete alert <alert-id-1> <alert-id-2> <alert-id-3> ...
```
