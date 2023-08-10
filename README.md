# synctl
Command to manage synthetic test, location and credential easily

# Table of Contents
- [Features](#features)
- [Installation](#installation)
    - [Linux & Mac OS](#linux--mac-os)
    - [Windows](#windows)
- [Config an Instana Backend](#config-an-instana-backend)
    - [Use a config file (Recommended)](#use-a-config-file-recommended)
    - [Run command with --host and --token](#run-command-with---host-and---token-no-need-to-set-a-config-file)
    - [Use environment vars](#use-environment-vars)
- [Query Synthetic Test](#query-synthetic-test)
- [Create a synthetic test](#create-a-synthetic-test)
    - [Create command usage](#create-command-usage)
    - [Examples](#examples)
        - [Create an API Simple test](#create-a-simple-ping-test)
        - [Create an API Script test](#create-an-api-script-test)
        - [Create BrowserScript](#create-browserscript)
        - [Create WebpageScript](#create-webpagescript)
        - [Create WebpageAction](#create-webpageaction)
        - [Create Synthetic Test using json payload](#create-synthetic-test-using-json-payload)
- [Patch a Synthetic Test](#patch-a-synthetic-test)
- [Update a Synthetic Test](#update-a-synthetic-test)
- [Delete Synthetic test](#delete-synthetic-test)
- [Manage Application](#query-application)
    - [Get application list](#get-application-list)
- [Manage Synthetic Locations](#manage-synthetic-locations)
    - [Query synthetic location](#query-synthetic-location)
    - [Delete synthetic location](#delete-synthetic-location)
- [Manage Credentials](#manage-credentials)
    - [Display all credentials](#display-all-credentials)
    - [Create credential](#create-credential)
    - [Delete credential](#delete-credential)

# Features
- `query`/`create`/`delete`/`patch`/`update` synthetic test, support API Simple, API Script, Browser script, etc.
- `query`/`delete` synthetic location
- `query`/`create`/`delete` credential
- support multiple backend server

# Prerequisites
- [Python 3.6+](https://www.python.org/downloads/)
- [requests 2.28+](https://requests.readthedocs.io/en/latest/)

# Installation

### Linux & Mac OS
```
# depend on requests https://pypi.org/project/requests/
# use pip3 to install requests module
pip3 install requests
# or use python3 -m pip
/usr/bin/python3 -m pip install requests

# clone code and copy it to /usr/local/bin/
git clone https://github.com/instana/synthetic-synctl.git

cd synthetic-synctl
chmod +x synctl && cp synctl /usr/local/bin/synctl

# if no permissions, use sudo 
chmod +x synctl && sudo cp synctl /usr/local/bin/synctl
```

### Windows

To install python3 on Windows, see [link](https://www.python.org/downloads/windows/). To install git, see [link](https://github.com/git-guides/install-git#install-git-on-windows).


```
# install requests
python3 -m pip install requests

# clone the code
git clone https://github.com/instana/synthetic-synctl.git

cd <your-path>/synthetic-synctl
python3 synctl [options]
```


# Config an Instana Backend
`synctl` support three types of configurations:
- Use configurations file, default is `~/.synthetic/config.json`.
- Use `--host` and `--token` to specify the host and token.
- Use environment variables, export `SYN_SERVER_HOSTNAME`, `SYN_API_TOKEN`.

**Note:** The priority of configuration is command options > environment variables > config file.

### Use a config file (Recommended)

```
# set your backend host and token, and give it an alias name, and set it as default
synctl config set \
    --host "https://test-instana.pink.instana.rocks" \
    --token "Your Token" \
    --name "pink" \
    --default

# list configs
synctl config list

# set pink as default
synctl config use --name pink --default

# remove a config
synctl config remove --name pink
```
**Note:** By default, config file is `~/.synthetic/config.json`.

### Run command with --host <host> and --token <token>

```
# retrieve all tests with --host and --token
synctl get test --host "https://test-instana.pink.instana.rocks" --token <Your-Token>

# get all locations with host and token
synctl get location --host "https://test-instana.pink.instana.rocks" --token <Your-Token>
```

### Use environment vars

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


# Query Synthetic Test

```
# Display all tests
synctl get test

# get test by synthetic type
# HTTPAction(0), HTTPScript(1), BrowserScript(2) and WebpageScript(3) are supported
# use 0, 1, 2, 3 represent each type instead of HTTPAction, HTTPScript, BrowserScript 
# and WebpageScript for simple
synctl get test -t <type>

# get HTTPAction test, and specify its type 0
synctl get test -t 0


# get synthetic test result with --window-size, support [1, 60]m, [1-24]h
synctl get test --window-size 30m

synctl get test --window-size 6h

# show test details
synctl get test <id> --show-details

# other options, --save-script, --show-script, --show-json
synctl get test <id> --save-script
synctl get test <id> --show-script
synctl get test <id> --show-json
```

# Create a synthetic test

### Create command usage
```
synctl create test [options]

options:
    -t <int>, --type <int>              synthetic type: 0 HTTPAction, 1 HTTPScript, 2 BrowserScript, 3 WebpageScript, 4 WebpageAction
    --location id [id ...]              location id, support multiple locations id
    --label <string>                    friendly name of the Synthetic test
    --description, -d <string>          the description of synthetic test
    --frequency <int>                   the range is from 1 to 120 minute, default is 15
    --app-id, --application-id <id>     application id
    --url <url>                         HTTP request URL
    --operation <method>                HTTP request methods, GET, POST, HEAD, PUT, etc
    --headers <json>                    HTTP headers
    --body <string>                     HTTP Body
    -f, --from-file <file>              synthetic script, specify a file name
    --bundle <bundle>                   specify a zip file or use synthetic script encoded with base64
    --script-file <file-name>           bundle script entry file, e.g, myscript.js
    --retries <int>                     retry times, value is from [0, 2]
    --retry-interval <int>              set Retry Invertal, range is [1, 10]
    --follow-redirect <boolean>         to allow redirect, true by default
    --timeout <num>ms|s|m               set timeout, accept <number>(ms|s|m)
    --expect-status <int>               expected status code, synthetic test will fail if response status is not equal to it, default 200
    --expect-json <string>              An optional object to be used to check against the test response object
    --expect-match <string>             An optional regular expression string to be used to check the test response
    --expect-exists <string>            An optional list of property labels used to check if they are present in the test response object
    --expect-not-empty <string>         An optional list of property labels used to check if they are present in the test response object with a non-empty value
    --allow-insecure <boolean>          if set to true then allow insecure certificates
    --custom-properties <string>        An object with name/value pairs to provide additional information of the Synthetic test
    --browser <string>                  browser type, support chrome and firefox
    --record-video <boolean>            set true to record video
    --from-json <json>                  full synthetic test payload, specify a json file
    --key <key>                         set credential name
    --value <value>                     set credential value
```

## Examples  

### Create an API Simple test  

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

```

### Create an API script test  

```
# a simple API script
synctl create test -t 1 \
    --label "simple-api-script" \
    --from-file http-scripts/http-get.js \
    --location "$LOCATION" \
    --frequency 5

# create bundle test with a zip file
synctl create test -t 1 --label syn-bundle-zip-test \
    --bundle synthetic.zip \
    --script-file index.js \
    --location "$LOCATION" \
    --frequency 5

# create bundle test
synctl create test -t 1 --label "syn-bundle-test" \
    --bundle "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" \
    --script-file index.js \
    --location "$LOCATION" \
    --frequency 5
```

### Create BrowserScript  


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

### Create WebpageScript  


```
synctl create test -t 3 \
    --label "webpage-script-test" \
    --location "$LOCATION" --frequency 15 \
    --from-file side/webpage-script.side  \
    --browser chrome
```

### Create WebpageAction
```
synctl create test -t 4 \ 
    --label "browser-test-webpageaction" \
    --url "https://httpbin.org/get" \
    --location "$LOCATION" --frequency 5 \
    --record-video true
    --browser chrome
```

### Create Synthetic Test using json payload  

```
synctl create test -t <type> --from-json payload/api-script.json
```


**Note:** Support specify application id when create synthetic test, get an application id through command `synctl get app`.



# Patch a Synthetic Test
The command `patch` can be used to updates selected attributes of a Synthetic Test, only one attribute can be patched each time.


```
# set label to simple-ping
synctl patch test <synthetic-id> --label simple-ping

# set description to "This is a synthetic test"
synctl patch test <synthetic-id> --description "This is a synthetic test"

# set retries to 2
synctl patch test <synthetic-id> --retries 2

# set retry-interval to 5
synctl patch test <synthetic-id> --retry-interval 5

# set mark-synthetic-call to True
synctl patch test <synthetic-id> --mark-synthetic-call True
 
# set frequency to 5
synctl patch test <synthetic-id> --frequency 5

# set timeout to 120s
synctl patch test <synthetic-id> --timeout 120s

# disable synthetic test
synctl patch test <synthetic-id> --active false

# set operation to POST
synctl patch test <synthetic-id> --opertaion POST

# update synthetic script
# save script to local, script name is test <label>.js 
synctl get test <synthetic-id> --save-script

# edit script file, and update synthetic test with new script
synctl patch test <synthetic-id> --script-file simple-api-script.js

# update bundle test with a zip file
synctl patch test <synthetic-id> --bundle synthetic.zip

# update bundle test using base64 string
synctl patch test <synthetic-id> --bundle "UEsDBAoAAAAAAHltFlUAAAAAAAAAAAAAAAAEABwAbGliL1VUCQADlRcDY2izBGN1eAsAAQToAwAABOgDAABQSwMEFAAIAAgA1FkYVQAAAAAAAAAAVAMAAA8AHABsaWIvbXlzY3JpcHQuanNVVAkAA6CXBWOglwVjdXgLAAEE6AMAAAToAwAAlVPBbuIwEL3zFSOLQ5C65t5qVwIpB9RuVbW5R8YMidVgp56hWYT67zsOoUuLkFifEue9N2/eTGzwxLAHQ4SR4QN+QsS3rYuYKVsbpyZ3I0M7b2G99ZZd8MBIPHe+yiawH41AznQK3ry7yjACB+i6Ti8FoG3Y9N+tFAkN6iZUmfp1ftQNqJm1SASJB62pMBVOXNMZxzBextCJQ10hZ6pmbm+n09M6CX700mJch7gBQhNtDaa3/R9GEpwgrAeBC07GmdK0LFOl8u0C5lCasokm9Kt73FGmJEyukZ1VJ7fjVXTvQpAXnT8W+fNED11kJ40NQ0rxADtuEJY7kESK9CzjMK3roQ0eQP29TPQ8w4ExmO5ltYzdNCf+4Ae8HAK4+ac2UK4J8unT5i18kzg2xOYVgWxE9FQHvlq6EN7LJ+1C+PwFdGx2vGXXaOfJVTWTTED2qVg8lcXzYp6Xj7Pfefkwm+cPqQyFDXItG9Zv18fdaBNWW7GGf9oQmSTZfa95/CMSRM5fUEsHCJkl42ODAQAAVAMAAFBLAwQUAAgACAB5bRZVAAAAAAAAAAARAQAACQAcAG15dGVzdC5qc1VUCQADlRcDYxC7BGN1eAsAAQToAwAABOgDAABdjzEOwjAMRfeewooYgoTSHcTCFdjY2mAVozQOiRkK4u6kVEjgzXp+/0u/CSjwBMEiB4oDvGAPGW93ymiNawP17TgVnymJuxaz3jWN51g4oAs8WJM4bc0GVmWKckEh7yqp1p90xqWBOCr556NDQiM+OKJKzPhUsdZD12MoSl6gVo/SZQHhz+p50ne9rfcbUEsHCA5zkg+OAAAAEQEAAFBLAQIeAwoAAAAAAHltFlUAAAAAAAAAAAAAAAAEABgAAAAAAAAAEAD/QQAAAABsaWIvVVQFAAOVFwNjdXgLAAEE6AMAAAToAwAAUEsBAh4DFAAIAAgA1FkYVZkl42ODAQAAVAMAAA8AGAAAAAAAAQAAAP+BPgAAAGxpYi9teXNjcmlwdC5qc1VUBQADoJcFY3V4CwABBOgDAAAE6AMAAFBLAQIeAxQACAAIAHltFlUOc5IPjgAAABEBAAAJABgAAAAAAAEAAAD/gRoCAABteXRlc3QuanNVVAUAA5UXA2N1eAsAAQToAwAABOgDAABQSwUGAAAAAAMAAwDuAAAA+wIAAAAA"

# set url to https://www.ibm.com
synctl patch test <synthetic-id> --url https://www.ibm.com

# set followredirect to true
synctl patch test <synthetic-id> --follow-redirect true

# set expectStatus to 200
synctl patch test <synthetic-id> --expect-status 200

# set validationString to synthetic-test
synctl patch test <synthetic-id> --validation-string "synthetic-test"

# set entry file of bundle test
synctl patch test <synthetic-id> --entry-file bundle-test/index.js

```

# Update a Synthetic Test


```
# get synthetic configuration
synctl get test <synthetic-id> --show-json

# edit json and update
synctl update test <synthetic-id> --from-data 'json data'
```


# Delete synthetic test

```
# delete a synthetic test
synctl delete test <synthetic-id>

# delete several synthetic tests
synctl delete test <synthetic-id-1> n<synthetic-id-2> <synthetic-id-3> ...


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


# Manage Application

### Get application list

```
# get all application
synctl get app

# filter application by --name-filter, or pattern that application name contains
synctl get app --name-filter <application-name>

# then create test with application id
synctl create test -t 0 --app-id <application-id> ...
```

# Manage Synthetic Locations

### Query synthetic location

```
# Display Synthetic Location
synctl get location

# Display synthetic location details
synctl get location <location-id> --show-details
```

### Delete synthetic location

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

### Create credential

```
synctl create cred --key <key-name> --value <value>
```

### Delete credential

```
synctl delete cred <key-name>
```
