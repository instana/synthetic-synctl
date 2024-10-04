#!/usr/bin/env python3

#  (c) Copyright IBM Corp. 2023
#  (c) Copyright Instana Inc. 2023

"""Command Line Tool for Synthetic Monitoring to Manage Synthetic Test and Locations Easily"""
import argparse
from base64 import b64encode, b64decode
# from getpass import getpass
import json
from pathlib import Path
import os
import re
import signal
import sys

import tarfile
import getpass
import math
# import textwrap
import time
from datetime import datetime

import requests
import urllib3

from synctl.__version__ import __version__

VERSION = __version__

# disable warning when certificate is self signed
# InsecureRequestWarning: Unverified HTTPS request is being made to host 'some url'.
# Adding certificate verification is strongly advised.
# See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


HTTPAction_TYPE = "HTTPAction"
HTTPScript_TYPE = "HTTPScript"

BrowserScript_TYPE = "BrowserScript"
WebpageScript_TYPE = "WebpageScript"
WebpageAction_TYPE = "WebpageAction"
SSLCertificate_TYPE = "SSLCertificate"

# supported Synthetic type
synthetic_type = (
    HTTPAction_TYPE,     # 0
    HTTPScript_TYPE,     # 1
    BrowserScript_TYPE,  # 2
    WebpageScript_TYPE,  # 3
    WebpageAction_TYPE,  # 4
    SSLCertificate_TYPE  # 5
)

SYN_TEST = "test"
SYN_LOCATION = "location"
SYN_LO = "lo"  # short for location
SYN_APPLICATION = "application"
SYN_APP = "app"  # short for application
SYN_CRED = "cred"  # short for credentials
SYN_ALERT = "alert"  # short for smart alerts
SYN_RESULT = "result"
POP_SIZE = "pop-size"
POP_COST = "pop-cost"

POSITION_PARAMS = "commands"
OPTIONS_PARAMS = "options"

NOT_APPLICABLE = "N/A"

NORMAL_CODE, ERROR_CODE = (0, 1)

TOO_MANY_REQUEST_ERROR="Too Many Requests"

def _status_is_200(status):
    return status == 200

def _status_is_201(status):
    return status == 201

def _status_is_204(status):
    return status == 204

def _status_is_400(status):
    return status == 400

def _status_is_403(status):
    return status == 403

def _status_is_404(status):
    return status == 404

def _status_is_429(status):
    return status == 429

def show_version():
    """show synctl version"""
    print(f"synctl version: {VERSION}")


def general_helper() -> None:
    m = """Usage: synctl <command> [options]

Options:
    -h, --help          show this help message and exit
    --version, -v       show version

Commands:
    config              manage configuration file
    create              create a Synthetic test, credential and smart alert
    get                 get Synthetic tests, locations, credentials, smart alert, pop-size and pop-cost
    patch               patch a Synthetic test
    update              update a Synthetic test and smart alert
    delete              delete Synthetic tests, locations credentials and smart alert

Use "synctl <command> -h/--help" for more information about a command.
    """
    print(m)

def identify_hyphen():
    sys.argv = [
        " " + a if a.startswith('-') and not a.startswith('--') and len(a) > 2 and sys.argv[2] == 'alert' else a
        for a in sys.argv
    ]

def validate_args(args):
    seen = set()
    for item in args:
        if item in seen and (item.startswith("--") or item.startswith("-")):
            print(f"{item} should not be provided multiple times")
            sys.exit()
        else:
            seen.add(item)

COMMAND_CONFIG = 'config'
COMMAND_CREATE = 'create'
COMMAND_GET = 'get'
COMMAND_DELETE = 'delete'
COMMAND_PATCH = 'patch'
COMMAND_UPDATE = 'update'

CONFIG_USAGE = """synctl config {set,list,use,remove} [options]

examples:
# set a default instana backend to connect
synctl config set --host <host> --token <token> --name <name>"""

CREATE_USAGE = """synctl create test/cred/alert [options]

examples:
# create an API Simple
synctl create test -t 0 --label simple-ping-test --url <url> --location <id> --frequency 5

# create an API Script
synctl create test -t 1 --label script-test --script script-name.js --location <id>

# create an API Script bundle
synctl create test -t 1 --label script-bundle-test --bundle file.zip --bundle-entry-file index.js --location <id>
synctl create test -t 1 --label script-bundle-test --bundle <base64> --bundle-entry-file index.js --location <id>

# create browserscript
synctl create test -t 2 --label browserscript-test --script browserscripts/api-sample.js --browser firefox --location <id>

# create browserscript bundle
synctl create test -t 2 --label "browserscript-bundle-test" --bundle "file.zip" --bundle-entry-file mytest.js --browser chrome --location <id>
synctl create test -t 2 --label "browserscript-bundle-test" --bundle "<base64>" --bundle-entry-file mytest.js --browser chrome --location <id>

# create webpagescript
synctl create test -t 3 --label "webpagescript-test" --script side/webpage-script.side --browser chrome --location <id>

# create WebpageAction
synctl create test -t 4 --label "webpageaction-test" --url <url> --location <id> --frequency 5 --record-video true

# create SSLCertificate test
synctl create test -t 5 --label "ssl-test" --hostname <host> --port <port> --remaining-days-check 30 --location <id> 

# create a credential
synctl create cred --key MY_PASS --value password123

# create a smart alert
synctl create alert --name "Smart-alert" --alert-channel "$ALERT_CHANNEL" --test "$SYNTHETIC_TEST" --violation-count 2
"""

GET_USAGE = """synctl get {location,lo,test,application,app,cred,alert, pop-size, pop-cost} [id] [options]

examples:
# display all tests
synctl get test

# display all locations
synctl get location
synctl get lo

# show test details
synctl get test <id> --show-details

# display all credentials
synctl get cred

# Display all alert
synctl get alert

# Estimate the size of the PoP hardware configuration
synctl get pop-size

# Estimate the cost of Instana-hosted Pop
synctl get pop-cost"""

PATCH_USAGE = """synctl patch test id [options]

examples:
# set active to false
synctl patch test <syn-id> --active false

# update frequency to 5, run test every 5min
synctl patch test <id> --frequency 5"""

UPDATE_USAGE = """synctl update {test,alert} <id> [options]

examples:
# update synthetic test/smart alert using file
synctl get test/alert <id>  --show-json > <filename>.json
edit <filename>.json
synctl update test/alert <id> -f <filename>.json

# update test with multiple options
synctl update test <test-id> --label "simple-ping" \\
    --description "this is a test example" \\
    --url "https://www.ibm.com" \\
    --location "$LOCATION1" "$LOCATION2" "$LOCATION3" ... \\
    --retries 2 \\
    --retry-interval 2 \\
    --follow-redirect true \\
    --timeout 1m \\
    --frequency 5 \\
    --app-id "$APP_ID" \\
    --custom-properties "key1=value1,key2=value2"

# update alert with multiple options
synctl update alert <alert-id> --name "Smart-alert" \\
    --alert-channel "$ALERT_CHANNEL1" "$ALERT_CHANNEL2" "$ALERT_CHANNEL3" ... \\
    --test "$SYNTHETIC_TEST1" "$SYNTHETIC_TEST2" "$SYNTHETIC_TEST3" ... \\
    --violation-count 2 \\
    --severity warning

# enable/disable a smart alert
synctl update alert <alert-id> --enable
synctl update alert <alert-id> --disable
"""

DELETE_USAGE = """synctl delete {location,lo,test,cred,alert} [id...] [options]

examples:
# delete a test
synctl delete test <id>

# delete a location
synctl delete location <location-id>

# delete all tests which label match regex
synctl delete test --match-regex "^simple-ping-"

# delete all tests with no locations
synctl delete test --no-locations

# delete all tests on a location
synctl delete test --match-location <location-id>

# delete a credential
synctl delete cred <credential-name>

# delete a smart alert
synctl delete alert <alert-id>"""


class Base:

    def __init__(self) -> None:
        self.auth = {
            "host": "",
            "token": ""
        }
        self.insecure = False

    def set_auth(self, auth: dict):
        """set auth"""
        if auth is not None:
            self.auth = auth
        else:
            print("auth is None")

    def set_host_token(self, new_host=None, new_token=None):
        if new_host is not None and new_token is not None:
            self.auth["host"] = new_host.rstrip('/')
            self.auth["token"] = new_token
        else:
            print("both --host and --token are required")

    def check_host_and_token(self, host, token):
        if host == "" or token == "":
            self.exit_synctl(ERROR_CODE, "host or token should not be empty")

    def set_insecure(self, verify=False):
        self.insecure = verify

    def get_insecure(self):
        return self.insecure

    def fill_space(self, s: str, length: int = 25) -> str:
        l = len(s)
        if l < length:
            return s + ' '*(length-l)
        else:
            return s

    def get_home_path(self) -> str:
        """return home directory"""
        return str(Path.home())

    def ask_answer(self, message: str) -> bool:
        answer = input(message + " [yes/no] ")
        if answer == "yes" or answer == "y":
            return True
        else:
            return False

    def merge_json(self, dict1: dict, dict2: dict) -> dict:
        """merge two dicts"""
        for i in dict2.keys():
            dict1[i] = dict2[i]
        return dict1

    def format_time(self, milliseconds):
        """convert milliseconds to format like \'Wed Aug  2 16:50:25 2023\'"""
        if milliseconds is not None and isinstance(milliseconds, int):
            return time.ctime(milliseconds/1000)
        else:
            return milliseconds

    def format_frequency(self, frequency):
        if frequency > 60:
            hours = frequency // 60
            minutes = frequency % 60
            test_frequency = str(hours)+"h" if minutes == 0 else str(hours)+"h"+str(minutes)+"m"
        else:
            test_frequency = str(frequency)+"m"
        return test_frequency

    def change_time_format(self, t, return_date_only=False):
        """format time to YYYY-MM-DD, HH:MM:SS"""
        date_time = datetime.fromtimestamp(t/1000)
        if return_date_only == False:
            formatted_date_time = date_time.strftime("%Y-%m-%d, %H:%M:%S")
        else:
            formatted_date_time = date_time.strftime("%Y-%m-%d")

        return formatted_date_time

    def exit_synctl(self, error_code=-1, message=''):
        """exit synctl"""
        if message != '':
            print(message)
        sys.exit(error_code)

class PopConfiguration(Base):
    def __init__(self) -> None:
        Base.__init__(self)
        self.agent = {
            "cpuLimit": 1500,
            "memLimit": 768,
            "imageSize": 600,
        }
        self.k8ssensor = {
            "cpuLimit": 500,
            "memLimit": 1536,
            "imageSize": 80,
        }
        self.controller = {
            "cpuLimit": 300,
            "memLimit": 300,
            "imageSize": 900,
        }
        self.redis = {
            "cpuLimit": 300,
            "memLimit": 200,
            "imageSize": 500,
        }
        self.http = {
            "testCount": 2000,
            "frequency": 1,
            "cpuLimit": 300,
            "memLimit" : 500,
            "imageSize": 400,
        }
        self.javascript = {
            "testCount": 20,
            "frequency": 1,
            "cpuLimit": 800,
            "memLimit": 300,
            "imageSize": 400,
        }
        self.browserscript = {
            "testCount": 5,
            "frequency": 5,
            "cpuLimit": 4000,
            "memLimit": 3000,
            "imageSize": 1500,
        }
        self.ism = {
            "testCount": 2000,
            "frequency": 1,
            "cpuLimit": 300,
            "memLimit": 500,
            "imageSize": 350,
        }

        self.factors = {
            "browserTest": 1,
            "APIScript": 0.042,
            "APISimple": 0.025,
            "SSLTest": 0.025
        }

    def ask_question(self,question, options=None):
        answer = input(question)
        if options:
            while answer not in options:
                print("Invalid input")
                answer = input(question)
        return answer

    def get_api_simple_test(self):
        api_simple_test = {}
        api_simple_test["testCount"] = int(self.ask_question("How many API Simple tests do you want to create? (0 if no) "))
        if api_simple_test["testCount"] > 0:
            while True:
                api_simple_test["frequency"] = int(self.ask_question("What is the test frequency for your API Simple tests? (1-120) "))
                if api_simple_test["frequency"] > 0 and api_simple_test["frequency"] <= 120:
                    break
                else:
                    print("frequency is not valid, it should be in [1,120]")
        return api_simple_test

    def get_api_script_test(self):
        api_script_test = {}
        api_script_test["testCount"] = int(self.ask_question("How many API Script tests do you want to create? (0 if no) "))
        if api_script_test["testCount"] > 0:
            while True:
                api_script_test["frequency"] = int(self.ask_question("What is the test frequency for your API Script tests? (1-120) "))
                if api_script_test["frequency"] > 0 and api_script_test["frequency"] <= 120:
                    break
                else:
                    print("frequency is not valid, it should be in [1,120]")
        return api_script_test

    def get_browser_script_test(self):
        browser_script_test = {}
        browser_script_test["testCount"] = int(self.ask_question("How many Browser tests (Webpage Action, Webpage Script and BrowserScript) do you want to create? (0 if no) "))
        if browser_script_test["testCount"] > 0:
            while True:
                browser_script_test["frequency"] = int(self.ask_question("What is the test frequency for Browser tests? (1-120) "))
                if browser_script_test["frequency"] > 0 and browser_script_test["frequency"] <= 120:
                    break
                else:
                    print("frequency is not valid, it should be in [1,120]")
        return browser_script_test

    def get_ssl_test(self):
        ssl_test = {}
        ssl_test["testCount"] = int(self.ask_question("How many ISM tests (SSLCertificate) do you want to create? (0 if no) "))
        if ssl_test["testCount"] > 0:
            while True:
                ssl_test["frequency"] = int(self.ask_question("What is the test frequency for ISM tests (SSLCertificate)? (1-1440) "))
                if ssl_test["frequency"] > 0 and ssl_test["frequency"] <= 1440:
                    break
                else:
                    print("frequency is not valid, it should be in [1,1440]")
        return ssl_test

    def size_estimate(self, user_tests, default_frequency, user_frequency, default_tests):
        pod_estimate = int(user_tests * default_frequency) / int(user_frequency * default_tests)
        return math.ceil(pod_estimate)

    def test_exec_estimate(self, tests, frequency, loc):
        #The total test executions per month(30 days)
        return int(tests * ((30 * 24 * 60) / frequency) * loc)

    def pop_size_estimate(self):
        pop_estimate_size = {}
        print("Please answer below questions for estimating the self-hosted PoP hardware size:\n")
        try:
            while True:
                pop_estimate_size["api_simple"] = self.get_api_simple_test()
                if pop_estimate_size["api_simple"]["testCount"] == 0:
                    pop_estimate_size["http_pod_count"] = 0
                    break
                elif pop_estimate_size["api_simple"]["testCount"] < 0:
                    print("Invalid input")
                else:
                    pop_estimate_size["http_pod_count"] = int(self.size_estimate(pop_estimate_size["api_simple"]["testCount"], self.http["frequency"], pop_estimate_size["api_simple"]["frequency"], self.http["testCount"]))
                    break

            while True:
                pop_estimate_size["api_script"] = self.get_api_script_test()
                if pop_estimate_size["api_script"]["testCount"] == 0:
                    pop_estimate_size["javascript_pod_count"] = 0
                    break
                elif pop_estimate_size["api_script"]["testCount"] < 0:
                    print("Invalid input")
                else:
                    pop_estimate_size["javascript_pod_count"] = int(self.size_estimate(pop_estimate_size["api_script"]["testCount"], self.javascript["frequency"], pop_estimate_size["api_script"]["frequency"], self.javascript["testCount"]))
                    break

            while True:
                pop_estimate_size["browser_script"] = self.get_browser_script_test()
                if pop_estimate_size["browser_script"]["testCount"] == 0:
                    pop_estimate_size["browserscript_pod_count"] = 0
                    break
                elif pop_estimate_size["browser_script"]["testCount"] < 0:
                    print("Invalid input")
                else:
                    pop_estimate_size["browserscript_pod_count"] = int(self.size_estimate(pop_estimate_size["browser_script"]["testCount"], self.browserscript["frequency"], pop_estimate_size["browser_script"]["frequency"], self.browserscript["testCount"]))
                    break

            while True:
                pop_estimate_size["ssl"] = self.get_ssl_test()
                if pop_estimate_size["ssl"]["testCount"] == 0:
                    pop_estimate_size["ism_pod_count"] = 0
                    break
                elif pop_estimate_size["ssl"]["testCount"] < 0:
                    print("Invalid input")
                else:
                    pop_estimate_size["ism_pod_count"] = int(self.size_estimate(pop_estimate_size["ssl"]["testCount"], self.ism["frequency"], pop_estimate_size["ssl"]["frequency"], self.ism["testCount"]))
                    break

            pop_estimate_size["agent"] = self.ask_question("Do you want to install the Instana-agent to monitor your PoP? (Y/N) ", options=["Y", "N", "y", "n"])
            while True:
                if pop_estimate_size["agent"] in ["y", "Y"]:
                    pop_estimate_size["worker_nodes"] = int(self.ask_question("How many worker nodes in your kubernetes cluster? "))
                    if pop_estimate_size["worker_nodes"] <= 0:
                        print("Number of worker nodes must be greater than 0.")
                    else:
                        pop_estimate_size["k8ssensor_pod_count"] = 3 if pop_estimate_size["worker_nodes"] >= 3 else 1
                        break
                else:
                    pop_estimate_size["worker_nodes"] = 0
                    pop_estimate_size["k8ssensor_pod_count"] = 0
                    break

            if pop_estimate_size["api_simple"]["testCount"] == 0 and pop_estimate_size["api_script"]["testCount"] == 0 and pop_estimate_size["browser_script"]["testCount"] == 0:
                pop_estimate_size["controller_pod_count"] = 0
                pop_estimate_size["redis_pod_count"] = 0
            else:
                pop_estimate_size["controller_pod_count"] = 1
                pop_estimate_size["redis_pod_count"] = 1

            pop_estimate_size["cpu"] = self.controller["cpuLimit"] * pop_estimate_size["controller_pod_count"] + self.redis["cpuLimit"] * pop_estimate_size["redis_pod_count"] + pop_estimate_size["http_pod_count"] * self.http["cpuLimit"] + \
                  pop_estimate_size["javascript_pod_count"] * self.javascript["cpuLimit"] + pop_estimate_size["browserscript_pod_count"] * self.browserscript["cpuLimit"] + \
                  pop_estimate_size["worker_nodes"] * self.agent["cpuLimit"] + self.k8ssensor["cpuLimit"] * pop_estimate_size["k8ssensor_pod_count"] + \
                  pop_estimate_size["ism_pod_count"] * self.ism["cpuLimit"]

            pop_estimate_size["memory"] = pop_estimate_size["http_pod_count"] * self.http["memLimit"] + pop_estimate_size["javascript_pod_count"] * self.javascript["memLimit"] + \
                     pop_estimate_size["browserscript_pod_count"] * self.browserscript["memLimit"] + pop_estimate_size["worker_nodes"] * self.agent["memLimit"] +  \
                     self.k8ssensor["memLimit"] * pop_estimate_size["k8ssensor_pod_count"] +  self.controller["memLimit"] * pop_estimate_size["controller_pod_count"] + \
                     self.redis["memLimit"] * pop_estimate_size["redis_pod_count"] + pop_estimate_size["ism_pod_count"] * self.ism["memLimit"]

            pop_estimate_size["disk_size"] = pop_estimate_size["http_pod_count"] * self.http["imageSize"] + pop_estimate_size["javascript_pod_count"] * self.javascript["imageSize"] + \
                        pop_estimate_size["browserscript_pod_count"] * self.browserscript["imageSize"] + pop_estimate_size["controller_pod_count"] * self.controller["imageSize"] + \
                        pop_estimate_size["redis_pod_count"] * self.redis["imageSize"] + pop_estimate_size["worker_nodes"] * self.agent["imageSize"] + \
                        pop_estimate_size["k8ssensor_pod_count"] * self.k8ssensor["imageSize"] + pop_estimate_size["ism_pod_count"] * self.ism["imageSize"]

            return pop_estimate_size
        except ValueError as e:
            self.exit_synctl(ERROR_CODE, f"Exception: {e}")

    def pop_cost_estimate(self):
        cost_estimate = {}

        print("List price for 1 unit(part number) is $12/month and 1 part number entitles 1000 Resource Units (RU) per month.")
        print("The relationship between RU and test executions are:\n"
        "   ● 1 API Simple test executed = 0.025 RU \n"
        "   ● 1 ISM        test executed = 0.025 RU \n"
        "   ● 1 API Script test executed = 0.042 RU \n"
        "   ● 1 Browser    test executed = 1 RU \n")
        print("The minimum quantity per month is 30 part numbers, priced at $360.")

        print("\nPlease answer below questions for estimating the cost of Synthetic tests running on Instana hosted PoPs.\n")
        try:
            while True:
                cost_estimate["locations"] = int(self.ask_question("How many managed locations will be used? "))
                if cost_estimate["locations"] > 0:
                    while True:
                        cost_estimate["api_simple"] = self.get_api_simple_test()
                        if cost_estimate["api_simple"]["testCount"] == 0:
                            cost_estimate["api_simple_test_exec"] = 0
                            cost_estimate["api_simple_res"] = 0
                            break
                        elif cost_estimate["api_simple"]["testCount"] < 0:
                            print("Invalid input")
                        else:
                            cost_estimate["api_simple_test_exec"] = self.test_exec_estimate(cost_estimate["api_simple"]["testCount"], cost_estimate["api_simple"]["frequency"], cost_estimate["locations"])
                            # resource units per month
                            cost_estimate["api_simple_res"] = cost_estimate["api_simple_test_exec"] * self.factors["APISimple"]
                            break

                    while True:
                        cost_estimate["api_script"] = self.get_api_script_test()
                        if cost_estimate["api_script"]["testCount"] == 0:
                            cost_estimate["api_script_test_exec"] = 0
                            cost_estimate["api_script_res"] = 0
                            break
                        elif cost_estimate["api_script"]["testCount"] < 0:
                            print("Invalid input")
                        else:
                            cost_estimate["api_script_test_exec"] = self.test_exec_estimate(cost_estimate["api_script"]["testCount"], cost_estimate["api_script"]["frequency"], cost_estimate["locations"])
                            cost_estimate["api_script_res"] = cost_estimate["api_script_test_exec"] * self.factors["APIScript"]
                            break

                    while True:
                        cost_estimate["browser_script"] = self.get_browser_script_test()
                        if cost_estimate["browser_script"]["testCount"] == 0:
                            cost_estimate["browserscript_test_exec"] = 0
                            cost_estimate["browserscript_res"] = 0
                            break
                        elif cost_estimate["browser_script"]["testCount"] < 0:
                            print("Invalid input")
                        else:
                            cost_estimate["browserscript_test_exec"] = self.test_exec_estimate(cost_estimate["browser_script"]["testCount"], cost_estimate["browser_script"]["frequency"], cost_estimate["locations"])
                            cost_estimate["browserscript_res"] = cost_estimate["browserscript_test_exec"] * self.factors["browserTest"]
                            break

                    while True:
                        cost_estimate["ssl_test"] = self.get_ssl_test()
                        if cost_estimate["ssl_test"]["testCount"] == 0:
                            cost_estimate["ssl_test_exec"] = 0
                            cost_estimate["ssl_test_res"] = 0
                            break
                        elif cost_estimate["ssl_test"]["testCount"] < 0:
                            print("Invalid input")
                        else:
                            cost_estimate["ssl_test_exec"] = self.test_exec_estimate(cost_estimate["ssl_test"]["testCount"], cost_estimate["ssl_test"]["frequency"], cost_estimate["locations"])
                            cost_estimate["ssl_test_res"] = cost_estimate["ssl_test_exec"] * self.factors["SSLTest"]
                            break

                    # Total resource units per month
                    cost_estimate["total_resource"] = cost_estimate["api_simple_res"] + cost_estimate["api_script_res"] + cost_estimate["browserscript_res"] + cost_estimate["ssl_test_res"]

                    # Total parts per month
                    cost_estimate["total_parts"] = round(cost_estimate["total_resource"]/1000, 0)

                    # Total estimated cost per month
                    # List price for 1 unit = $12
                    cost_estimate["total_cost"] = cost_estimate["total_parts"] * 12

                    if cost_estimate["total_cost"] < 360:
                        cost_estimate["total_resource"] = 30000
                        cost_estimate["total_parts"] = 30.0
                        cost_estimate["total_cost"] = 360.0

                    return cost_estimate
                else:
                    print("number of locations cannot be less than 1")
        except ValueError as e:
            self.exit_synctl(ERROR_CODE,f"Exception: {e}")

    def print_estimated_pop_size(self):

        pop_estimate_size = self.pop_size_estimate()

        test_counts = [format(pop_estimate_size[test_type]["testCount"], ',') for test_type in ["api_simple", "api_script", "browser_script", ]]
        max_commas = max(str(test_count).count(',') for test_count in test_counts)
        max_label_length = max(len(str(pop_estimate_size["api_simple"]["testCount"])), len(str(pop_estimate_size["api_script"]["testCount"])),
                               len(str(pop_estimate_size["browser_script"]["testCount"])), len(pop_estimate_size["agent"])+2) + max_commas
        fixed_spaces1=" "*3
        fixed_spaces2=" "*7
        print("\nYour requirement is:")
        if pop_estimate_size["api_simple"]["testCount"] > 0:
            print(f'{fixed_spaces1}API    Simple: {pop_estimate_size["api_simple"]["testCount"]:<{max_label_length},}{fixed_spaces2}Frequency: {pop_estimate_size["api_simple"]["frequency"]}min')
        else:
            print(f'{fixed_spaces1}API    Simple: {pop_estimate_size["api_simple"]["testCount"]:<{max_label_length}}')
        if pop_estimate_size["api_script"]["testCount"] > 0:
            print(f'{fixed_spaces1}API    Script: {pop_estimate_size["api_script"]["testCount"]:<{max_label_length},}{fixed_spaces2}Frequency: {pop_estimate_size["api_script"]["frequency"]}min')
        else:
            print(f'{fixed_spaces1}API    Script: {pop_estimate_size["api_script"]["testCount"]:<{max_label_length}}')
        if pop_estimate_size["browser_script"]["testCount"] > 0:
            print(f'{fixed_spaces1}Browser  Test: {pop_estimate_size["browser_script"]["testCount"]:<{max_label_length},}{fixed_spaces2}Frequency: {pop_estimate_size["browser_script"]["frequency"]}min')
        else:
            print(f'{fixed_spaces1}Browser  Test: {pop_estimate_size["browser_script"]["testCount"]:<{max_label_length}}')
        if pop_estimate_size["ssl"]["testCount"] > 0:
            print(f'{fixed_spaces1}ISM      Test: {pop_estimate_size["ssl"]["testCount"]:<{max_label_length},}{fixed_spaces2}Frequency: {pop_estimate_size["ssl"]["frequency"]}min')
        else:
            print(f'{fixed_spaces1}ISM      Test: {pop_estimate_size["ssl"]["testCount"]:<{max_label_length}}')

        agent_yes = "Yes" if pop_estimate_size["agent"] in ["y", "Y"] else "No"
        if pop_estimate_size["agent"].upper() == "Y":
            print(f'{fixed_spaces1}Install Agent: {agent_yes:<{max_label_length}}{fixed_spaces2}Worker Nodes: {pop_estimate_size["worker_nodes"]}')
        else:
            print(f'{fixed_spaces1}Install Agent: {agent_yes:<{max_label_length}}')

        print("\nThe estimated sizing is:")
        print(f'{fixed_spaces1}CPU:     {pop_estimate_size["cpu"]:,}m')
        print(f'{fixed_spaces1}Memory:  {pop_estimate_size["memory"]:,}Mi')
        print(f'{fixed_spaces1}Disk:    {pop_estimate_size["disk_size"]/1000:,}GB')

        print("\nThe recommended engine pods:")
        print(f'{fixed_spaces1}http           playback engines: {pop_estimate_size["http_pod_count"]}')
        print(f'{fixed_spaces1}javascript     playback engines: {pop_estimate_size["javascript_pod_count"]}')
        print(f'{fixed_spaces1}browserscript  playback engines: {pop_estimate_size["browserscript_pod_count"]}')
        print(f'{fixed_spaces1}ISM            playback engines: {pop_estimate_size["ism_pod_count"]}')

    def print_estimated_cost(self):

        cost_estimate = self.pop_cost_estimate()
        print(f'\nThe total executions per month:\n    API   Simple executions: {cost_estimate["api_simple_test_exec"]:,}')
        print(f'    API   Script executions: {cost_estimate["api_script_test_exec"]:,}')
        print(f'    Browser Test executions: {cost_estimate["browserscript_test_exec"]:,}')
        print(f'    ISM     Test executions: {cost_estimate["ssl_test_exec"]:,}\n')

        print(f'The total cost estimated:\n    Cost per month is: ${cost_estimate["total_cost"]:,}')
        print(f'    Number of part numbers per month is: {cost_estimate["total_parts"]:,}')
        print(f'    Resource Units per month is: {cost_estimate["total_resource"]:,}')

class ConfigurationFile(Base):
    def __init__(self) -> None:
        Base.__init__(self)

        HOME_PATH = self.get_home_path()
        self.CONFIG_FOLDER = HOME_PATH + "/.synthetic/"
        self.CONFIG_FILE = HOME_PATH + "/.synthetic/config.json"

        # create config folder if not exists
        self.__initial_config_folder()
        self.__initial_config_file()

        self.config_json = self.__read_config_file()

    def __initial_config_folder(self):
        if not os.path.isdir(self.CONFIG_FOLDER):
            os.mkdir(self.CONFIG_FOLDER)

    def __initial_config_file(self):
        default_config_json = []

        if not os.path.isfile(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as fp:
                json.dump(default_config_json,
                          fp,
                          ensure_ascii=True,
                          indent=4)

    def __check_config_file(self):
        # path exists or not
        is_exist = os.path.isfile(self.CONFIG_FILE)
        if not is_exist:
            return False
        return True

    def __read_config_file(self):
        if self.__check_config_file():
            with open(self.CONFIG_FILE, "r+", encoding="utf-8") as file1:
                # Reading from a file
                info = file1.read()
                return json.loads(info)
        else:
            print("no config file")

    def __write_json_to_file(self):
        """write config to ~/.synthetic/config.json"""
        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as config_file1:
            json.dump(self.config_json, config_file1,
                      ensure_ascii=True, indent=4)

    def print_config_file(self, name="", show_token=False):
        """print all config info"""
        if show_token is True:
            print(self.fill_space("NAME".upper()),
                  self.fill_space("Default".upper(), 13),
                  self.fill_space("Token".upper()),
                  "Hostname".upper())
            if name != "" and name != "default" and name is not None:
                for _, item in enumerate(self.config_json):
                    encoded_token = b64encode(item["token"].encode()).decode()
                    if item["name"] == name:
                        print(self.fill_space(item["name"]),
                              self.fill_space(str(item["default"]), 13),
                              self.fill_space(encoded_token),
                              item["host"])
            else:
                # show all
                for _, item in enumerate(self.config_json):
                    encoded_token = b64encode(item["token"].encode()).decode()
                    print(self.fill_space(item["name"]),
                          self.fill_space(str(item["default"]), 13),
                          self.fill_space(encoded_token),
                          item["host"])
        else:
            print(self.fill_space("NAME".upper()),
                  self.fill_space("Default".upper(), 13),
                  "Hostname".upper())
            if name != "" and name != "default" and name is not None:
                for _, item in enumerate(self.config_json):
                    if item["name"] == name:
                        print(self.fill_space(item["name"]),
                              self.fill_space(str(item["default"]), 13),
                              item["host"])
            else:
                # show all
                for _, item in enumerate(self.config_json):
                    print(self.fill_space(item["name"]),
                          self.fill_space(str(item["default"]), 13),
                          item["host"])

    def __check_if_already_in_config(self, name: str) -> bool:
        for _, item in enumerate(self.config_json):
            if item["name"] == name:
                return True

        return False

    def __remove_right_slash(self, host_name):
        """remove right slash of a host"""
        return host_name.rstrip('/')

    def add_an_item_to_config(self, name, host, token, set_default=False):
        """add a new config"""
        if name is None or host is None or token is None:
            print("name, host, and token should not be none")
        elif name == "" or host == "" or token == "":
            print("name, host, and token must not be none")
        elif self.__check_if_already_in_config(name):
            # update it
            self.update_an_item(name, self.__remove_right_slash(
                host), token, set_default=set_default)
        else:
            self.config_json.append({
                "name": name,
                "host": self.__remove_right_slash(host),
                "token": token,
                "default": False
            })

            if set_default is True:
                self.set_env_to_default(name)
            elif len(self.config_json) == 1 and set_default is False:
                self.config_json[0]["default"] = True

            self.__write_json_to_file()

    def remove_an_item_from_config(self, name):
        """remove a config"""
        if_default = False
        for index, item in enumerate(self.config_json):
            if name == item["name"]:
                if_default = item["default"] is True
                del self.config_json[index]
        # if delete the default, set 0 to default
        if if_default is True and len(self.config_json) > 0:
            self.config_json[0]["default"] = True

        self.__write_json_to_file()

    def update_an_item(self, name, host, token, set_default=False):
        """update a config"""
        for _, item in enumerate(self.config_json):
            if item["name"] == name:
                item["host"] = host
                item["token"] = token
        if set_default is True:
            self.set_env_to_default(name)
        self.__write_json_to_file()

    def set_env_to_default(self, name):
        """set config to default"""
        set_default = False
        for _, item in enumerate(self.config_json):
            if name == item["name"]:
                item["default"] = True
                set_default = True
            else:
                item["default"] = False
        # name not exist and set the first to default
        if set_default is False and len(self.config_json) > 0:
            self.config_json[0]["default"] = True

        self.__write_json_to_file()

    def get_config_json_data(self):
        """get configuration content"""
        return self.config_json

    def get_default_config(self):
        for item in self.config_json:
            if item["default"] is True:
                return {
                    "host": self.__remove_right_slash(item["host"]),
                    "token": item["token"]
                }
        if len(self.config_json) > 0:
            return {
                "host": self.__remove_right_slash(self.config_json[0]["host"]),
                "token": self.config_json[0]["token"]
            }
        else:
            self.exit_synctl(ERROR_CODE, "no configurations")

    def get_auth_by_name(self, name):
        if len(self.config_json) > 0:
            for item in self.config_json:
                if item["name"] == name:
                    return {
                        "host": self.__remove_right_slash(item["host"]),
                        "token": item["token"]
                    }
            raise ValueError(f"no config named \"{name}\"")
        else:
            return {"host": "", "token": ""}


class Authentication(ConfigurationFile):
    def __init__(self) -> None:
        ConfigurationFile.__init__(self)

    def __get_from_environment_var(self):
        self.auth["host"] = os.getenv('SYN_SERVER_HOSTNAME')
        self.auth["token"] = os.getenv('SYN_API_TOKEN')

    def __check_syn_env(self) -> bool:
        if os.getenv('SYN_SERVER_HOSTNAME') is not None and os.getenv('SYN_API_TOKEN') is not None:
            return True
        return False

    def get_auth(self, env_name=None):
        """get auth from Global Variable or config file"""
        if self.__check_syn_env():
            self.__get_from_environment_var()
            return self.auth
        elif env_name is not None:
            return ConfigurationFile.get_auth_by_name(self, name=env_name)
        else:
            return ConfigurationFile.get_default_config(self)


class SyntheticConfiguration(Base):

    def __init__(self, syn_type: str = "HTTPAction", bundle_type: bool = False) -> None:
        Base.__init__(self)
        self.syn_test_config = {
            # Unique identifier of the Synthetic test resource.
            # "id": "",
            # Friendly name of the Synthetic test resource.
            "label": "default-test-label",
            # "tenantId": "instanalocal",
            # The description of the Synthetic test.
            "description": "This is a Synthetic test",
            # Indicates if the Synthetic test is started or not. The default is true.
            "active": True,  # required
            # Unique identifier of the Application Perspective.
            "applicationId": None,

            # customProperties An object with name/value pairs to provide additional information of the Synthetic test.
            "customProperties": {},
            # locations It is an array of the PoP location IDs where the Synthetic tests are located.
            "locations": [],
            # modifiedAt The test last updated time, following RFC3339 standard.
            # modifiedBy The user identifier who updated the test resource.

            # playbackMode Defines how the Synthetic test should be executed across multiple PoPs.
            # Possible values are Simultaneous or Staggered. Simultaneous Synthetic tests run at all locations simultaneously.
            # Staggered Synthetic tests run from a different location at each interval.
            # This property is optional, and its default value is Simultaneous.
            "playbackMode": "Simultaneous",
            # testFrequency How often the playback for a Synthetic test is scheduled.
            # The unit of the testFrequency parameter is minute.
            # The default is every 15 minutes.
            # The range is from 1 minute to 120 minutes.
            # For SSLCertificate test the range is 1 minute to 1440 minutes. Default is 1440 minutes.
            "testFrequency": "15",

            # An object which has two properties: syntheticType and the corresponding configuration object
            "configuration": {
                # Flag used to control if HTTP calls will be marked as Synthetic calls/endpoints in Instana backend,
                # so they can be ignored when calculating service and application KPIs, users can also check "Hide
                # Synthetic Calls" checkbox to hide/show them in UI.
                "markSyntheticCall": True,
                # An integer type from 0 to 2, 0 by default.
                # It indicates how many attempts (max 2) will be allowed to get a successful connection (not necessarily a successful result).
                # Failures like socket hangups, gateway timeouts, and DNS lookup fails cause retries, but 404's 400's, do not.
                "retries": 0,
                # The time interval between retries in seconds. The default is 1s, max is 10s.
                "retryInterval": "1",
                # The timeout to be used by the PoP playback engines running the test.
                # Values in integer followed by time unit (ms, s, m).
                # If timeout is not provided the playback engine will use its own timeout value.
                "timeout": "",
            }
        }

        http_action_conf = {
            # The type of the Synthetic test.
            # Supported values are HTTPAction, HTTScript, BrowserScript, WebpageAction, WebpageScript, and DNSAction.
            # The locations assigned to execute this Synthetic test must support this syntheticType, i.e
            # the location's playbackCapabilities property.
            "syntheticType": HTTPAction_TYPE,

            # The URL is being tested. It is required.
            "url": "",
            # An operation being used must be one of GET, HEAD, OPTIONS, PATCH, POST, PUT, and DELETE. By default, it is GET.
            "operation": "GET",
            # headers An object with header/value pairs
            # header The header to be sent in operation. It should not contain the terminating ':' character.
            # value The value of the header.
            "headers": {},
            # body The body content to send with the operation.
            "body": "",
            # validationString An expression to be evaluated.
            "validationString": "",
            # followRedirect A boolean type, true by default; to allow redirect.
            "followRedirect": True,
            # allowInsecure A boolean type, true by default;
            # if set to true then allow insecure certificates (expired, self-signed, etc).
            "allowInsecure": True,
            # expectStatus An integer type, by default, the Synthetic passes for any 2XX status code.
            # This forces just one status code to cause a pass, including what would normally be a fail, for example, a 404.
            "expectStatus": None,  # default None
            # expectJson An optional object to be used to check against the test response object.
            "expectJson": {},  # dict
            # expectMatch An optional regular expression string to be used to check the test response.
            "expectMatch": "",
            # expectExists An optional list of property labels used to check if
            # they are present in the test response object.
            "expectExists": None,  # list
            # expectNotEmpty An optional list of property labels used to check if
            # they are present in the test response object with a non-empty value.
            "expectNotEmpty": None  # list
        }

        http_script_conf = {
            "syntheticType": HTTPScript_TYPE,
            "script": "",  # api script
            "retries": 0,  # [0,2]
            "retryInterval": 5,
            "scriptType": "Basic"  # ["Jest", "Basic"]
        }

        http_bundle_conf = {
            "syntheticType": HTTPScript_TYPE,
            "scripts": {
                "scriptFile": "index.js",
                "bundle": ""  # base64 string
            },  # bundle
            "retries": 0,  # [0,2]
            "retryInterval": 5,
            "scriptType": "Basic"
        }

        browser_script_conf = {
            "syntheticType": BrowserScript_TYPE,
            "script": "",  # api script
            "retries": 0,  # [0,2]
            "retryInterval": 5,
            "scriptType": "Basic"
        }

        browser_bundle_conf = {
            "syntheticType": "BrowserScript",
            "scripts": {
                "scriptFile": "index.js",
                "bundle": ""
            },
            "browser": "firefox",
        }

        # syntheticType BrowserScript
        # self.browser_script_conf = {
        #     "scripts": {
        #         "scriptFile": "index.js",
        #         "bundle": ""
        #     },
        #     "syntheticType": "BrowserScript",
        #     "browser": "firefox",
        # }

        # syntheticType WebpageScript
        self.webpage_script_conf = {
            "script": "",
            "syntheticType": "WebpageScript",
            "browser": "chrome",
            "recordVideo": False
        }

        # syntheticType WebpageAction
        self.webpage_action_conf = {
            "syntheticType": "WebpageAction",
            "browser": "chrome",
            "recordVideo": False
        }

        # syntheticType SSLCertificate
        self.SSL_certificate_conf = {
            "syntheticType": "WebpageAction",
            "hostname": ""
        }

        self.script_type = [HTTPScript_TYPE, BrowserScript_TYPE]
        if syn_type in [HTTPAction_TYPE, HTTPScript_TYPE, BrowserScript_TYPE, WebpageScript_TYPE, WebpageAction_TYPE]:
            self.syn_type = syn_type
        if bundle_type is True:
            self.is_bundle = True
        if syn_type == HTTPAction_TYPE:
            self.syn_test_config["configuration"] = self.merge_json(
                self.syn_test_config["configuration"], http_action_conf)

        if bundle_type is True and syn_type == HTTPScript_TYPE:
            self.syn_test_config["configuration"] = self.merge_json(
                self.syn_test_config["configuration"], http_bundle_conf)
        elif bundle_type is False and syn_type == HTTPScript_TYPE:
            self.syn_test_config["configuration"] = self.merge_json(
                self.syn_test_config["configuration"], http_script_conf)

        # BrowserScript support simple script and bundle type
        if bundle_type is True and syn_type == BrowserScript_TYPE:
            self.syn_test_config["configuration"] = self.merge_json(
                self.syn_test_config["configuration"], browser_bundle_conf)
        elif bundle_type is False and syn_type == BrowserScript_TYPE:
            self.syn_test_config["configuration"] = self.merge_json(
                self.syn_test_config["configuration"], browser_script_conf)

        if syn_type == WebpageScript_TYPE:
            self.syn_test_config["configuration"] = self.merge_json(
                self.syn_test_config["configuration"], self.webpage_script_conf)

        if syn_type == WebpageAction_TYPE:
            self.syn_test_config["configuration"] = self.merge_json(
                self.syn_test_config["configuration"], self.webpage_action_conf)

        # set syntheticType
        self.syn_test_config["configuration"]["syntheticType"] = syn_type

    def __ensure_script_not_empty(self):
        if "script" in self.syn_test_config["configuration"]:
            if self.syn_test_config["configuration"]["script"] is None or self.syn_test_config["configuration"]["script"] == "":
                self.exit_synctl(ERROR_CODE, "Error: script cannot be empty")

    def __ensure_bundle_script_not_empty(self):
        if "scripts" in self.syn_test_config["configuration"]:
            bundle_scripts = self.syn_test_config["configuration"]["scripts"]["bundle"]
            if bundle_scripts is None or bundle_scripts == "":
                self.exit_synctl(ERROR_CODE, "Error: bundle script cannot be empty")

    def set_application_id(self, applications: list):
        """set application id"""
        if applications is None:
            applications = []
        if len(applications) > 0:
            self.syn_test_config["applications"] = applications

    def set_websites(self, websites: list):
        """set website application"""
        if websites is None:
            websites = []
        if len(websites) > 0:
            self.syn_test_config["websites"] = websites

    def set_mobile_apps(self, mobile_apps: list):
        """set mobile app"""
        if mobile_apps is None:
            mobile_apps = []
        if len(mobile_apps) > 0:
            self.syn_test_config["mobileApps"] = mobile_apps

    def set_label(self, label: str = "default-test-name") -> None:
        """set label"""
        if label != "":
            self.syn_test_config["label"] = label

    def set_description(self, description: str = "This is default description"):
        """set description"""
        if description != "":
            self.syn_test_config["description"] = description

    def set_active(self, active: bool):
        """set active default True"""
        pass

    def set_custom_properties(self, custom_prop: dict):
        """customProperties"""
        if custom_prop is not None and isinstance(custom_prop, dict):
            self.syn_test_config["customProperties"] = custom_prop

    def set_validation_string(self, validation_string):
        if validation_string is not None or validation_string != "":
            self.syn_test_config["configuration"]["validationString"] = validation_string

    def set_locations(self, locations: list = None):
        """locations"""
        if locations is None:
            locations = []
        if len(locations) > 0:
            self.syn_test_config["locations"] = locations

    def set_timeout(self, timeout: int) -> None:
        """timeout <number>(ms|s|m)"""
        self.syn_test_config["configuration"]["timeout"] = timeout

    def __get_ssl_frequency(self, frequency: int) -> int:
        if frequency > 0 and frequency <= 1440:
            return frequency
        else:
            return 1440

    def __get_test_frequency(self, frequency: int) -> int:
        if frequency > 0 and frequency <= 120:
            return frequency
        else:
            return 15

    def set_frequency(self, syn_type, frequency: int = 15) -> None:
        """set test frequency"""
        if syn_type == 5: # test ssl certificate
            self.syn_test_config["testFrequency"] = self.__get_ssl_frequency(frequency)
        else:
            self.syn_test_config["testFrequency"] = self.__get_test_frequency(frequency)

    def set_ping_url(self, url: str) -> None:
        """url"""
        if self.syn_type in (HTTPAction_TYPE, WebpageAction_TYPE) and url != "":
            self.syn_test_config["configuration"]["url"] = url

    def set_ping_operation(self, method: str = "GET"):
        """operation"""
        valid_methods = ["GET", "HEAD", "POST", "PUT", "DELETE",
                         "CONNECT", "OPTIONS", "TRACE", "PATCH"]
        if method is not None and method.upper() in valid_methods:
            self.syn_test_config["configuration"]["operation"] = method.upper()
        else:
            print(f"{method} is not allowed")

    def set_ping_headers(self, headers: dict):
        """headers"""
        if headers is not None:
            self.syn_test_config["configuration"]["headers"] = headers

    def set_ping_body(self, body: str):
        """body"""
        if body:
            self.syn_test_config["configuration"]["body"] = body

    def set_api_script_script(self, script_str: str) -> None:
        """set script"""
        if script_str is None:
            self.exit_synctl(ERROR_CODE, f"script content: {script_str}")

        if self.syn_type in (HTTPScript_TYPE, WebpageScript_TYPE, BrowserScript_TYPE) and script_str != "":
            self.syn_test_config["configuration"]["script"] = script_str

        # if self.syn_type == WebpageScript_TYPE and script_str != "":
        #     self.syn_test_config["configuration"]["script"] = script_str

    def get_api_script_script(self) -> str:
        """return script"""
        return self.syn_test_config["configuration"]["script"]

    def set_api_bundle_script(self, script_str: str, script_file: str = "index.js") -> None:
        """set bundle script and scriptFile"""
        if script_str is None:
            self.exit_synctl(ERROR_CODE, "bundle script is None")

        if self.syn_type in self.script_type and self.is_bundle is True:
            self.syn_test_config["configuration"]["scripts"]["bundle"] = script_str
            self.syn_test_config["configuration"]["scripts"]["scriptFile"] = script_file

    def set_mark_synthetic_call(self, mark):
        """markSyntheticCall"""
        pass

    def set_retries(self, retry):
        """retries"""
        if retry >= 0 and retry <= 2:
            self.syn_test_config["configuration"]["retries"] = retry
        else:
            raise ValueError("retry should be [0, 2]")

    def set_retry_interval(self, interval: int):
        """retryInterval"""
        if interval is None:
            interval = 1
        if interval > 0 and interval < 10:
            self.syn_test_config["configuration"]["retryInterval"] = interval

    def set_follow_redirect(self, follow_redirect):
        """set followRedirect"""
        if follow_redirect.lower() == "false":
            self.syn_test_config["configuration"]["followRedirect"] = False
        if follow_redirect.lower() == "true":
            self.syn_test_config["configuration"]["followRedirect"] = True

    def set_expect_status(self, expect_status: int) -> None:
        """set expectStatus for HTTPAction"""
        if expect_status is None:
            self.syn_test_config["configuration"]["expectStatus"] = None
            return
        if expect_status > 0:
            self.syn_test_config["configuration"]["expectStatus"] = expect_status
        else:
            self.syn_test_config["configuration"]["expectStatus"] = 200

    def set_expect_json(self, expect_json: dict):
        """set expectJson"""
        if expect_json:
            self.syn_test_config["configuration"]["expectJson"] = expect_json

    def set_expect_match(self, expect_match: str):
        """set expectMatch"""
        if expect_match:
            self.syn_test_config["configuration"]["expectMatch"] = expect_match

    def set_expect_exists(self, expect_exists: list):
        """set expectExists"""
        if expect_exists:
            self.syn_test_config["configuration"]["expectExists"] = expect_exists

    def set_expect_not_empty(self, expect_not_empty: list):
        """set expectNotEmpty"""
        if expect_not_empty:
            self.syn_test_config["configuration"]["expectNotEmpty"] = expect_not_empty

    def set_allow_insecure(self, allow_insecure):
        if allow_insecure is None:
            allow_insecure = True
        if allow_insecure == 'false':
            self.syn_test_config["configuration"]["allowInsecure"] = False
        if allow_insecure == 'true' or allow_insecure is True:
            self.syn_test_config["configuration"]["allowInsecure"] = True

    def set_browser_type(self, browser):
        """browser type"""
        if browser:
            self.syn_test_config["configuration"]["browser"] = browser

    def set_record_video(self, record_video):
        if record_video is not None:
            self.syn_test_config["configuration"]["recordVideo"] = record_video

    def set_host(self, hostname):
        if hostname is not None:
            self.syn_test_config["configuration"]["hostname"] = hostname

    def set_port(self, port):
        if port is not None:
            self.syn_test_config["configuration"]["port"] = port

    def set_remaining_days(self, remaining_days):
        if remaining_days is not None:
            self.syn_test_config["configuration"]["daysRemainingCheck"] = remaining_days

    def read_js_file(self, file_name: str) -> str:
        """read javascript file"""
        try:
            with open(file_name, "r+", encoding="utf-8") as file1:
                # Reading from a file
                info = file1.read()
                return info
        except FileNotFoundError as not_found_e:
            self.exit_synctl(ERROR_CODE, not_found_e)

    def get_test_conf_ins(self):
        if len(self.syn_test_config["locations"]) == 0:
            raise ValueError("no location, add a location for test")
        return self.syn_test_config  # dict

    def loads_from_json_file(self, json_file_name):
        try:
            with open(json_file_name, "r", encoding="utf-8") as json_file1:
                json_payload = json_file1.read()
                self.syn_test_config = json.loads(json_payload)
        except FileNotFoundError as not_found_e:
            self.exit_synctl(ERROR_CODE, not_found_e)

    def is_zip_file(self, file_name):
        """check zip file name"""
        if file_name is not None and isinstance(file_name, str):
            return file_name.endswith('.zip')

    def read_zip_file_to_base64(self, file_name):
        """read zip file and encode with base64"""
        with open(file_name, 'rb') as file1:
            zip_content_byte = file1.read()
            zip_content_byte_base64 = b64encode(zip_content_byte)
            zip_content_base64_str = zip_content_byte_base64.decode('utf-8')
            # self.set_api_bundle_script(zip_content_base64_str)
            return zip_content_base64_str

    def get_json(self):
        """return payload as json"""
        if len(self.syn_test_config["locations"]) == 0:
            self.exit_synctl(ERROR_CODE, "Error: no location, set --location <location-id> at least a location")

        # script should not be empty
        self.__ensure_script_not_empty()
        # bundle script should not be empty
        self.__ensure_bundle_script_not_empty()

        return json.dumps(self.syn_test_config)


class CredentialConfiguration(Base):
    def __init__(self):
        Base.__init__(self)
        self.credential_config = {
            "credentialName": "",
            "credentialValue": ""
        }

    def set_credential_name(self, key):
        self.credential_config["credentialName"] = key

    def set_credential_value(self, value):
        self.credential_config["credentialValue"] = value

    def set_credential_applications(self, applications: list):
        self.credential_config["applications"] = applications

    def set_credential_websites(self, websites: list):
        self.credential_config["websites"] = websites

    def set_credential_mobile_apps(self, mobile_apps):
        self.credential_config["mobileApps"] = mobile_apps

    def get_json(self):
        """return payload as json"""
        if len(self.credential_config["credentialName"]) == 0:
            self.exit_synctl(ERROR_CODE, "Error: no credential name, set --key <credential-name>")
        elif len(self.credential_config["credentialValue"]) == 0:
            self.exit_synctl(ERROR_CODE, "Error: no credential value, set --value <credential-value> ")

        result = json.dumps(self.credential_config)
        return result

class SyntheticCredential(Base):
    
    def __init__(self) -> None:
        Base.__init__(self)
        self.payload = None

    def set_cred_payload(self, payload=None):
        if payload is None:
            print("payload should not be none")
        else:
            self.payload = payload

    def create_credential(self):
        """create credential"""
        cred_payload = self.payload
        data = json.loads(cred_payload)
        cred_key = data["credentialName"]

        self.check_host_and_token(self.auth["host"], self.auth["token"])
        host = self.auth["host"]
        token = self.auth["token"]

        credential = self.retrieve_credentials()

        create_url = f"{host}/api/synthetics/settings/credentials/"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"apiToken {token}"
        }
        try:
            if cred_key not in credential:
                create_cred_res = requests.post(create_url,
                                                headers=headers,
                                                data=cred_payload,
                                                timeout=60,
                                                verify=self.insecure)
                if _status_is_201(create_cred_res.status_code):
                    print(f"credential \"{cred_key}\" created")
                elif _status_is_400(create_cred_res.status_code):
                    print(f'Create Error: {create_cred_res}\n',
                          create_cred_res.json())
                else:
                    print('Create credential failed, status code:',
                          create_cred_res.status_code)
            else:
                print("Credential already exists")
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")

    def retrieve_credentials(self, show_details=False):
        self.check_host_and_token(self.auth["host"], self.auth["token"])
        host = self.auth["host"]
        token = self.auth["token"]

        retrieve_url = f"{host}/api/synthetics/settings/credentials/"
        if show_details is True:
            retrieve_url = f"{host}/api/synthetics/settings/credentials/associations"

        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"apiToken {token}"
        }
        try:
            cred_result = requests.get(retrieve_url,
                                       headers=headers,
                                       timeout=60,
                                       verify=self.insecure)

            if _status_is_200(cred_result.status_code):
                if len(cred_result.content) == 0:
                    return {}
                else:
                    data = json.loads(cred_result.content.decode())
                    return data
            else:
                self.exit_synctl(ERROR_CODE, f'get cred failed, status code: {cred_result.status_code}')
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")

    def retrieve_a_credential(self, cred):
        self.check_host_and_token(self.auth["host"], self.auth["token"])
        host = self.auth["host"]
        token = self.auth["token"]

        retrieve_url = f"{host}/api/synthetics/settings/credentials/associations/{cred}"

        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"apiToken {token}"
        }
        try:
            cred_result = requests.get(retrieve_url,
                                       headers=headers,
                                       timeout=60,
                                       verify=self.insecure)

            if _status_is_200(cred_result.status_code):
                if len(cred_result.content) == 0:
                    return {}
                else:
                    data = json.loads(cred_result.content.decode())
                    return data
            else:
                self.exit_synctl(ERROR_CODE, f'get cred failed, status code: {cred_result.status_code}')
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")

    def delete_a_credential(self, cred):
        """Delete a credential"""
        self.check_host_and_token(self.auth["host"], self.auth["token"])
        if cred is None:
            print("credential should not be empty")
            return

        credential = self.retrieve_credentials()

        host = self.auth["host"]
        token = self.auth["token"]

        delete_url = f"{host}/api/synthetics/settings/credentials/{cred}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"apiToken {token}"
        }
        try:
            if cred in credential:
                delete_res = requests.delete(delete_url,
                                             headers=headers,
                                             timeout=60,
                                             verify=self.insecure)
                if _status_is_204(delete_res.status_code):
                    print(f'credential \"{cred}\" deleted')
                elif _status_is_429(delete_res.status_code):
                    print(TOO_MANY_REQUEST_ERROR)
                else:
                    print(
                        f"Fail to delete {cred}, status code {delete_res.status_code}")
            else:
                self.exit_synctl(ERROR_CODE, f"no credential {cred}")
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")

    def delete_credentials(self, cred_list):
        if cred_list is None:
            cred_list = []
        if len(cred_list) == 0:
            self.exit_synctl(ERROR_CODE, "no credential to delete")
        start_time = time.time()
        total_number = 0
        for cred in cred_list:
            self.delete_a_credential(cred)
            total_number += 1
        end_time = time.time()
        total_time = round((end_time-start_time)*1000, 3)
        print(f"total deleted: {total_number}, time used: {total_time}ms")

    def update_a_credential(self, cred):
        self.check_host_and_token(self.auth["host"], self.auth["token"])
        if cred is None:
            print("credential should not be empty")
            return

        credential = self.retrieve_credentials()

        host = self.auth["host"]
        token = self.auth["token"]

        # delete cred
        delete_url = f"{host}/api/synthetics/settings/credentials/{cred}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"apiToken {token}"
        }
        if cred in credential:
            delete_res = requests.delete(delete_url,
                                         headers=headers,
                                         timeout=60,
                                         verify=self.insecure)

            if _status_is_204(delete_res.status_code):
                pass
            else:
                self.exit_synctl(ERROR_CODE, f"Fail to delete {cred}")
        else:
            self.exit_synctl(ERROR_CODE, f"no credential {cred}")

        # create cred
        create_url = f"{host}/api/synthetics/settings/credentials/"

        credential = self.retrieve_credentials()
        cred_payload = self.payload

        if cred not in credential:
            create_cred_res = requests.post(create_url,
                                            headers=headers,
                                            data=cred_payload,
                                            timeout=60,
                                            verify=self.insecure)
            if _status_is_201(create_cred_res.status_code):
                print(f"Credential \"{cred}\" updated")
            else:
                print('Update credential failed, status code:',
                      create_cred_res.status_code)
        else:
            print("Credential already exists")

    def patch_applications(self, cred, applications):
        payload = {"applications": []}
        if applications is None:
            print("No applications")
            return
        else:
            payload["applications"] = applications
            self.__patch_a_credential(cred, json.dumps(payload))

    def patch_websites(self, cred, websites):
        payload = {"websites": []}
        if websites is None:
            print("No websites")
            return
        else:
            payload["websites"] = websites
            self.__patch_a_credential(cred, json.dumps(payload))

    def patch_mobile_apps(self, cred, mobile_apps):
        payload = {"mobileApps": []}
        if mobile_apps is None:
            print("No mobile applications")
            return
        else:
            payload["mobileApps"] = mobile_apps
            self.__patch_a_credential(cred, json.dumps(payload))

    def __patch_a_credential(self, cred, data):
        self.check_host_and_token(self.auth["host"], self.auth["token"])
        host = self.auth["host"]
        token = self.auth["token"]

        if cred is None:
            print("credential should not be empty")
            return

        patch_url = f"{host}/api/synthetics/settings/credentials/associations/{cred}"

        if data is None:
            self.exit_synctl(ERROR_CODE, "Patch Error:data cannot be empty")

        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"apiToken {token}"
        }
        try:
            patch_result = requests.patch(patch_url,
                                          headers=headers,
                                          data=data,
                                          timeout=60,
                                          verify=self.insecure)

            if _status_is_200(patch_result.status_code):
                print(f"{cred} updated")
            elif _status_is_400(patch_result.status_code):
                print(f'Patch Error: {patch_result}', patch_result.json())
            elif _status_is_429(patch_result.status_code):
                print(TOO_MANY_REQUEST_ERROR)
            else:
                print(
                    f'patch test {cred} failed, status code: {patch_result.status_code}')
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")

    def __get_max_cred_length(self, cred_list, max_len=60):
        label_len = 0
        if cred_list is not None and isinstance(cred_list, list):
            for cred in cred_list:
                if cred is not None and label_len < len(cred["credentialName"]):
                    label_len = len(cred["credentialName"]) + 5
        if label_len > 60:
            return 60
        else:
            return label_len if label_len > 10 else 10

    def print_credentials(self, credentials, show_details=False):
        if show_details is True:
            cred_length = self.__get_max_cred_length(credentials)
            created_length = 30
            modified_length = 30
            applications_length = 50
            websites_length = 50
            mobile_apps_length = 50
            print(self.fill_space("Credential Name".upper(), cred_length),
                  self.fill_space("Created".upper(), created_length),
                  self.fill_space("Modified".upper(), modified_length),
                  self.fill_space("Applications".upper(), applications_length),
                  self.fill_space("Websites".upper(), websites_length),
                  self.fill_space("Mobile Applications".upper(), mobile_apps_length))
            for cred in credentials:
                applications = cred.get("applications", "N/A")
                websites = cred.get("websites", "N/A")
                mobile_apps = cred.get("mobileApps", "N/A")

                print(self.fill_space(str(cred["credentialName"]), cred_length),
                      self.fill_space(str(self.change_time_format(cred["createdAt"])), created_length),
                      self.fill_space(str(self.change_time_format(cred["modifiedAt"])), modified_length),
                      self.fill_space(str(applications), applications_length),
                      self.fill_space(str(websites), websites_length),
                      self.fill_space(str(mobile_apps), mobile_apps_length))
        else:
            sorted_cred = sorted(credentials, key=str.lower)
            for cred in sorted_cred:
                print(cred)
            print(f"Total: {len(credentials)}")

    def print_a_credential(self, credential):
        """show a Synthetic credential details data"""
        print(self.fill_space("Name".upper(), 30), "Value".upper())
        for key, value in credential.items():
                if key == 'createdAt' or key == 'modifiedAt':
                    print(self.fill_space(key, 30), self.format_time(value))
                else:
                    print(self.fill_space(key, 30), value)


class SmartAlertConfiguration(Base):
    def __init__(self):
        Base.__init__(self)
        self.smart_alert_config = {
            # Unique identifier of the alert configuration..
            # "id": "",
            # Name for the synthetic alert configuration, which is used as the title of the event when triggered.
            "name": "default-Synthetics-Smart-Alert",
            # Description for the synthetic alert configuration, which is used as the details of the triggerd event.
            "description": "Synthetic test failed.",
            # The severity of the alert when triggered, which is either warning(5) or critical(10).
            "severity": 5,
            # syntheticTestIds: It is an array of the synthetic test IDs this alert configuration is applied to.
            "syntheticTestIds": [],
            # Indicates the type of rule this alert configuration is about.
            # The only alertType available so far is "failure", where the metric name "status" is expected.
            # This boolean metric requires no threshold to be specified, because value of status=0 indicates a test failure.
            "rule": {
                "alertType": 'failure',
            },
            # Defines the triggering condition in time, such as how many consecutive test failures are required to open an event.
            "timeThreshold": {
                "type": "violationsInSequence",
                "violationsCount": 1
            },
            # alertChannelIds: It is an array of alert channels defined in Instana.
            "alertChannelIds": [],
            "tagFilterExpression": {
                "type": 'EXPRESSION',
                "logicalOperator": 'AND',
                "elements": []
            }
        }

    def set_alert_name(self, name: str = "default-test-name") -> None:
        """set name"""
        if name != "":
            self.smart_alert_config["name"] = name

    def set_description(self, description: str = "This is default smart alert description"):
        """set description"""
        if description != "":
            self.smart_alert_config["description"] = description

    def set_severity(self, severity):
        """set severity"""
        severity_mapping = {"WARNING" : 5, "CRITICAL" :  10}
        if severity.upper() in ["WARNING", "CRITICAL"]:
            self.smart_alert_config["severity"] = severity_mapping.get(severity.upper())
        else:
            self.exit_synctl(ERROR_CODE, "severity should be warning or critical")

    def set_synthetic_tests(self, synthetic_tests: list = None):
        """set synthetic tests"""
        if synthetic_tests is None:
            synthetic_tests = []
        if len(synthetic_tests) > 0:
            self.smart_alert_config["syntheticTestIds"] = synthetic_tests

    def set_violations_count(self, violations_count):
        """set violations count"""
        if violations_count >= 1 and violations_count <= 12:
            self.smart_alert_config["timeThreshold"]["violationsCount"] = violations_count
        else:
            self.exit_synctl(ERROR_CODE, "violation count should be in [1,12]")

    def set_alert_channel(self, alert_channels):
        """set alert channels"""
        self.smart_alert_config["alertChannelIds"] = alert_channels

    def set_tag_filter_expression(self, tag_filter_json):
        """set tag filter expression"""
        if tag_filter_json is not None:
            self.smart_alert_config["tagFilterExpression"] = tag_filter_json
        else:
            self.exit_synctl(ERROR_CODE, "Tag-filter expression should not be None")

    def loads_from_json_file(self, json_file_name):
        try:
            with open(json_file_name, "r", encoding="utf-8") as json_file1:
                json_payload = json_file1.read()
                self.smart_alert_config = json.loads(json_payload)
        except FileNotFoundError as not_found_e:
            self.exit_synctl(ERROR_CODE, not_found_e)

    def get_json(self):
        """return payload as json"""
        if len(self.smart_alert_config["syntheticTestIds"]) == 0:
            self.exit_synctl(ERROR_CODE, "Error: no synthetic tests, set --test <test-id> at least a synthetic test")
        if len(self.smart_alert_config["alertChannelIds"]) == 0:
            self.exit_synctl(ERROR_CODE, "Error: no alert channel, set --alert-channel <alert-channel-id> at least an alert channel ")

        return  json.dumps(self.smart_alert_config)

class SyntheticLocation(Base):
    def __init__(self) -> None:
        Base.__init__(self)

    def retrieve_synthetic_locations(self, location_id=None):
        host = self.auth["host"]
        token = self.auth["token"]
        self.check_host_and_token(host, token)
        if location_id is None:
            request_url = f"{host}/api/synthetics/settings/locations"
        else:
            request_url = f"{host}/api/synthetics/settings/locations/{location_id}"

        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"apiToken {token}"
        }
        try:
            retrieve_res = requests.get(request_url,
                                        headers=headers,
                                        timeout=60,
                                        verify=self.insecure)

            if _status_is_200(retrieve_res.status_code):
                data = retrieve_res.json()

                if isinstance(data, dict):
                    return [data]
                else:
                    return data
            elif _status_is_429(retrieve_res.status_code):
                self.exit_synctl(ERROR_CODE, TOO_MANY_REQUEST_ERROR)
            else:
                self.exit_synctl(ERROR_CODE,
                    f"Failed to get locations, status code {retrieve_res.status_code}")
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")

    def get_location_summary_list(self,  page=1, page_size=200, window_size=60*60*1000):
        """curl --request POST 'http://{host}/api/synthetics/results/locationsummarylist'
        --header "Authorization: apiToken <YourToken>" -i
        --header "Content-Type: application/json"
        -d '{
             "pagincurlation": {
             "page": 1,
             "pageSize": 200
            },
             "timeFrame": {
             "to": 0,
             "windowSize": 3600000
            }
         }'
         """

        host = self.auth["host"]
        token = self.auth["token"]
        self.check_host_and_token(host, token)

        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"apiToken {token}"
        }

        summary_config = {
            "pagination": {
                "page": page,
                "pageSize": page_size
            },
            "timeFrame": {
                "to": 0,
                "windowSize": window_size
            }
        }
        request_url = f"{host}/api/synthetics/results/locationsummarylist"
        try:
            retrieve_res = requests.post(request_url,
                                         headers=headers,
                                         data=json.dumps(summary_config),
                                         timeout=60,
                                         verify=self.insecure)

            if _status_is_200(retrieve_res.status_code):
                data = retrieve_res.json()
                return data
            else:
                print('retrieve location summary list failed, status code:',
                      retrieve_res.status_code)
                return None
        except requests.exceptions.Timeout:
            print("retrieve location summary list failed")
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")
        return None

    def get_all_location_summary_list(self,  page=1):
        total_hits = 0
        summary_result = self.get_location_summary_list()
        if summary_result is not None:
            page = summary_result["page"] if page in summary_result else 1
            page_size = summary_result["pageSize"] if "pageSize" in summary_result else 200
            if "totalHits" in summary_result:
                total_hits = summary_result["totalHits"]

            if page_size >= total_hits:
                return summary_result
            else:
                total_pages = total_hits/page_size
                if (total_pages - round(total_pages)) > 0:
                    total_pages += 1
                for x in range(1, round(total_pages)):
                    summary_result = self.get_location_summary_list(page=x+1)
                return summary_result
        else:
            return None

    def __get_max_lo_label_length(self, loc_list, max_len=60):
        label_len = 15
        display_label_len = 15
        max_result = {
            "max_label": 35,
            "max_display_label": 50
        }
        if loc_list is not None and isinstance(loc_list, list):
            for lo in loc_list:
                if lo is not None and label_len < len(lo["label"]):
                    label_len = len(lo["label"])
                if lo is not None and display_label_len < len(lo["displayLabel"]):
                    display_label_len = len(lo["displayLabel"])
        max_result["max_label"] = label_len if label_len < 60 else 60
        max_result["max_display_label"] = display_label_len if display_label_len < 60 else 60
        return max_result

    def print_a_location_details(self, location_id, single_location, show_details=False):
        """show a Synthetic location details data"""
        if single_location is None or len(single_location) == 0 or location_id is None:
            print("no Synthetic location")
            return
        if show_details is True:
            a_single_location = single_location[0]
            print(self.fill_space("Name".upper(), 30), "value".upper())
            for key, value in a_single_location.items():
                if key == 'createdAt' or key == 'modifiedAt' or key == 'observedAt':
                    print(self.fill_space(key, 30), self.format_time(value))
                else:
                    print(self.fill_space(key, 30), value)

    def delete_a_synthetic_pop(self, pop_id=""):
        if pop_id != "":
            self.__delete_a_synthetic_location(location_id=pop_id)

    def __delete_a_synthetic_location(self, location_id=""):
        """delete a Synthetic location"""
        if location_id == "":
            print("location id should not be empty")
            return
        self.check_host_and_token(self.auth["host"], self.auth["token"])

        host = self.auth["host"]

        delete_url = f"{host}/api/synthetics/settings/locations/{location_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "apiToken %s" % (self.auth["token"])
        }
        try:
            r = requests.delete(delete_url,
                                headers=headers,
                                timeout=60,
                                verify=self.insecure)

            if _status_is_204(r.status_code):
                print(f'location \"{location_id}\" deleted')
            elif _status_is_404(r.status_code):
                print(f"{location_id} not found")
            elif _status_is_429(r.status_code):
                self.exit_synctl(ERROR_CODE, TOO_MANY_REQUEST_ERROR)
            else:
                print(f"Fail to delete {location_id}, status code {r.status_code}")
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")

    def delete_synthetic_locations(self, locations_list):
        if locations_list is None:
            locations_list = []

        if len(locations_list) == 0:
            print("no locations to delete")
            return

        for l in locations_list:
            self.__delete_a_synthetic_location(l)

    def print_synthetic_locations(self, locations, locations_summary):
        if locations is None:
            locations = []
        self.__print_pop(locations, locations_summary)

    def __print_pop(self, pop_data: list, pop_locations_summary):
        id_length = 22
        pop_version_length = 13
        status_length = 10
        loc_type_length = 10
        no_of_tests_length = 13
        max_length = self.__get_max_lo_label_length(pop_data)
        label_length = max_length["max_label"]
        display_label_length = max_length["max_display_label"]
        print(self.fill_space("ID".upper(), id_length),
              self.fill_space("Label".upper(), label_length),
              self.fill_space("DisplayLabel".upper(), display_label_length),
              self.fill_space("Type".upper(), loc_type_length),
              self.fill_space("Pop version".upper(), pop_version_length),
              self.fill_space("Status".upper(), status_length),
              self.fill_space("No. of Tests".upper(), no_of_tests_length),
              "Description".upper())
        if len(pop_data) > 0 and pop_locations_summary is not None:
            for pop in pop_data:
                for _, POP in enumerate(pop_locations_summary['items']):
                    if pop["id"] == POP['id']:
                        print(self.fill_space(pop["id"], id_length),
                              self.fill_space(pop['label'], label_length),
                              self.fill_space(pop['displayLabel'],
                                              display_label_length),
                              self.fill_space(pop['locationType'], loc_type_length),
                              self.fill_space(pop['popVersion'], pop_version_length),
                              self.fill_space(
                                  pop['status'], status_length),
                              self.fill_space(
                                  str(POP['linkedTests']), no_of_tests_length),
                              pop["description"])
        elif pop_locations_summary is None:
            for pop in pop_data:
                print(self.fill_space(pop["id"], id_length),
                      self.fill_space(pop['label'], label_length),
                      self.fill_space(pop['displayLabel'],
                                      display_label_length),
                      self.fill_space(pop['locationType'], loc_type_length),
                      self.fill_space(pop['popVersion'], pop_version_length),
                      self.fill_space(
                          pop['status'], status_length),
                      self.fill_space(
                          "N/A", no_of_tests_length),
                      pop["description"])
        else:
            print('no location')
        print('total:', len(pop_data))


class SyntheticTest(Base):
    """create, query, update and delete Synthetic test"""

    def __init__(self) -> None:
        Base.__init__(self)

        self.payload = None
        self.test_id = ""
        self.test_lists = []

    def set_synthetic_id(self, test_id):
        self.test_id = test_id

    def get_synthetic_id(self):
        return self.test_id

    def set_synthetic_payload(self, payload=None):
        if payload is None:
            print("payload should not be none")
        else:
            self.payload = payload

    def get_synthetic_payload(self):
        return self.payload

    def create_a_synthetic_test(self):
        """create a Synthetic test, test_payload is json"""
        test_payload = self.payload
        self.check_host_and_token(self.auth["host"], self.auth["token"])
        host = self.auth["host"]
        token = self.auth["token"]

        create_url = f"{host}/api/synthetics/settings/tests/"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"apiToken {token}"
        }
        try:
            create_res = requests.post(create_url,
                                       headers=headers,
                                       data=test_payload,
                                       timeout=60,
                                       verify=self.insecure)

            if _status_is_201(create_res.status_code):
                # extracting data in json format
                data = create_res.json()
                test_id = data["id"]
                test_label = data["label"]
                print(f"test \"{test_label}\" created, id is \"{test_id}\"" )
            elif _status_is_429(create_res.status_code):
                self.exit_synctl(ERROR_CODE, TOO_MANY_REQUEST_ERROR)
            else:
                print('create test failed, status code:', create_res.status_code)
                if create_res.text:
                    print(create_res.text)
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")


    def retrieve_a_synthetic_test(self, test_id=""):
        self.check_host_and_token(self.auth["host"], self.auth["token"])
        host = self.auth["host"]
        token = self.auth["token"]
        if id is None or test_id == "":
            print("test id should not be empty")
            return
        else:
            retrieve_url = f"{host}/api/synthetics/settings/tests/{test_id}"

        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"apiToken {token}"
        }
        try:
            result = requests.get(retrieve_url,
                                  headers=headers,
                                  timeout=60,
                                  verify=self.insecure)

            if _status_is_200(result.status_code):
                # extracting data in json format
                data = result.json()

                if isinstance(data, list):
                    self.test_lists = data
                    return data
                elif isinstance(data, dict):
                    self.test_lists = [data]
                    return [data]
                else:
                    print('unknown data:', data)
            elif _status_is_403(result.status_code):
                self.exit_synctl(error_code=ERROR_CODE,
                                 message='Insufficient access rights for resource')
            elif _status_is_404(result.status_code):
                self.exit_synctl(error_code=ERROR_CODE,
                                 message=f'test {test_id} not found')
            elif _status_is_429(result.status_code):
                self.exit_synctl(error_code=ERROR_CODE,
                                 message=TOO_MANY_REQUEST_ERROR)
            else:
                self.exit_synctl(ERROR_CODE,
                    f'get test {test_id} failed, status code: {result.status_code}')
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")

    def retrieve_all_synthetic_tests(self, syn_type=None):
        # API doc: https://instana.github.io/openapi/#operation/getSyntheticTests
        self.check_host_and_token(self.auth["host"], self.auth["token"])
        host = self.auth["host"]
        token = self.auth["token"]

        retrieve_url = f"{host}/api/synthetics/settings/tests/"

        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"apiToken {token}"
        }
        try:
            query_result = requests.get(retrieve_url,
                                        headers=headers,
                                        timeout=60,
                                        verify=self.insecure)
            if _status_is_200(query_result.status_code):
                # extracting data in json format
                data = query_result.json()
                syn_type_list = []
                if isinstance(data, list):
                    self.test_lists = data
                    for x in data:
                        if syn_type is not None and x is not None and x["configuration"]["syntheticType"] == syn_type:
                            syn_type_list.append(x)
                        if syn_type is None:
                            syn_type_list.append(x)
                    return syn_type_list
                elif isinstance(data, dict):
                    # only one test
                    self.test_lists = [data]
                    if syn_type is not None and data["configuration"]["syntheticType"] == syn_type:
                        return [data]
                    return []
                else:
                    self.exit_synctl(ERROR_CODE, f'unknown data: {data}')
            elif _status_is_403(query_result.status_code):
                self.exit_synctl(ERROR_CODE, 'Insufficient access rights for resource')
            elif _status_is_404(query_result.status_code):
                self.exit_synctl(ERROR_CODE, 'test not found')
            elif _status_is_429(query_result.status_code):
                self.exit_synctl(ERROR_CODE, TOO_MANY_REQUEST_ERROR)
            else:
                self.exit_synctl(ERROR_CODE, f'get test failed, status code: {query_result.status_code}')
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")

    def retrieve_test_results(self, test_id, page=1, page_size=200, window_size=60*60*1000):
        self.check_host_and_token(self.auth["host"], self.auth["token"])
        host = self.auth["host"]
        token = self.auth["token"]
        if id is None or test_id == "":
            print("test id should not be empty")
            return
        else:
            retrieve_url = f"{host}/api/synthetics/results/list"

        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"apiToken {token}"
        }
        summary_config = {"syntheticMetrics":["synthetic.metricsResponseTime","synthetic.metricsResponseSize", "status","synthetic.errors", "custom_metrics"],
                          "metrics": [{
                            "aggregation": "SUM",
                            "granularity": 600,
                            "metric": "synthetic.metricsStatus"
                        }],
                          "order":{
                              "by":"synthetic.metricsResponseTime",
                              "direction":"DESC"
                          },
                          "tagFilters":[{
                              "stringValue": test_id,
                              "name":"synthetic.testId",
                              "operator":"EQUALS"
                          }],
                          "pagination": {
                              "page": page,
                              "pageSize": page_size
                          },
                          "timeFrame": {
                              "to": 0,
                              "windowSize": window_size
                          }}
        try:
            result = requests.post(retrieve_url,
                                  headers=headers,
                                  data=json.dumps(summary_config),
                                  timeout=60,
                                  verify=self.insecure)
            if _status_is_200(result.status_code):
                data = result.json()
                return data
            else:
                self.exit_synctl(ERROR_CODE,
                                 f'retrieve test result list failed, status code:: {result.status_code}')
                return None
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")

    def __sort_test_result(self, result_list):
        """sort Synthetic result list by Starttime"""
        new_list = sorted(
            result_list, reverse=True, key=lambda result: result["metrics"]["response_time"][0][0] if result is not None else [])
        return new_list

    def retrieve_test_result_details(self, resultid, testid, HAR):
        self.check_host_and_token(self.auth["host"], self.auth["token"])
        host = self.auth["host"]
        token = self.auth["token"]
        test = self.retrieve_a_synthetic_test(testid)
        result = {}
        result["testid"] = testid
        result["resultid"] = resultid
        result["syntheticType"] = test[0]["configuration"]["syntheticType"]

        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"apiToken {token}"
        }
        try:
            if id is None or testid == "":
                print("test id should not be empty")
                return
            else:
                if test[0]["configuration"]["syntheticType"] in [HTTPAction_TYPE, HTTPScript_TYPE]:
                    retrieve_url_sub = f"{host}/api/synthetics/results/{testid}/{resultid}/detail?type=SUBTRANSACTIONS"
                    retrieve_url_logs = f"{host}/api/synthetics/results/{testid}/{resultid}/detail?type=LOGS"
                    result_sub = requests.get(retrieve_url_sub,
                                              headers=headers,
                                              timeout=60,
                                              verify=self.insecure)
                    result_logs = requests.get(retrieve_url_logs,
                                               headers=headers,
                                               timeout=60,
                                               verify=self.insecure)
                    if _status_is_200(result_sub.status_code):
                        result["sub"] = result_sub.json()["subtransactions"]
                    elif result_sub.status_code != 404:
                       print(f'get subtransactions for result {resultid} failed, status code: {result_sub.status_code}')
                    if _status_is_200(result_logs.status_code):
                        result["logs"] = result_logs.json()["logs"]
                    elif result_logs.status_code != 404:
                        print(f'get logs for result {resultid} failed, status code: {result_logs.status_code}')

                elif test[0]["configuration"]["syntheticType"] in  [BrowserScript_TYPE, WebpageScript_TYPE, WebpageAction_TYPE]:
                    if HAR:
                        retrieve_url_har = f"{host}/api/synthetics/results/{testid}/{resultid}/detail?type=HAR"
                        result_har = requests.get(retrieve_url_har,
                                                  headers=headers,
                                                  timeout=60,
                                                  verify=self.insecure)
                        if _status_is_200(result_har.status_code):
                            result["har"] = result_har.json()['har']
                        elif result_har.status_code != 404:
                            print(f'get har for result {resultid} failed, status code: {result_har.status_code}')
                    retrieve_url_image = f"{host}/api/synthetics/results/{testid}/{resultid}/file?type=IMAGES"
                    retrieve_url_videos = f"{host}/api/synthetics/results/{testid}/{resultid}/file?type=VIDEOS"
                    retrieve_url_logs = f"{host}/api/synthetics/results/{testid}/{resultid}/detail?type=LOGS"
                    result_logs = requests.get(retrieve_url_logs,
                                               headers=headers,
                                               timeout=60,
                                               verify=self.insecure)
                    result_image = requests.get(retrieve_url_image,
                                                headers=headers,
                                                timeout=60,
                                                verify=self.insecure)
                    result_videos = requests.get(retrieve_url_videos,
                                                 headers=headers,
                                                 timeout=60,
                                                 verify=self.insecure)
                    if _status_is_200(result_logs.status_code):
                        result["logs"] = result_logs.json()["logFiles"]
                    elif result_logs.status_code != 404:
                        print(f"get logs for result {resultid} failed, status code: {result_logs.status_code}")
                    if _status_is_200(result_image.status_code):
                        result["image"] = result_image.content
                    elif result_image.status_code != 404:
                        print(f'get image for result {resultid} failed, status code: {result_image.status_code}')
                    if _status_is_200(result_videos.status_code):
                        result["video"] = result_videos.content
                    elif result_videos.status_code != 404:
                        print(f'get videos for result {resultid} failed, status code: {result_videos.status_code}')
            return result
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")

    def get_all_test_results(self, test_id, window_size):
        total_hits = 0
        result_instance = SyntheticResult()
        window_size_ms = result_instance.get_window_size(window_size)
        result_list = self.retrieve_test_results(test_id,window_size=window_size_ms)
        if result_list is not None:
            page = result_list["page"] if "page" in result_list else 1
            page_size = result_list["pageSize"] if "pageSize" in result_list else 200
            if "totalHits" in result_list:
                total_hits = result_list["totalHits"]

            if page_size >= total_hits:
                return result_list
            else:
                total_pages = total_hits/page_size
                if (total_pages - round(total_pages)) > 0:
                    total_pages += 1
                for x in range(0, round(total_pages)):
                    result_list = self.retrieve_test_results(test_id=test_id,
                                                             page=x+1,
                                                             page_size=200,
                                                             window_size=window_size_ms)
                    return result_list
        else:
            return None

    def convert_milliseconds(self, time_ms):
        if time_ms > 60000:
            t = f"{time_ms / 60000:.2f}min"
        elif time_ms > 1000:
            t = f"{time_ms / 1000:.2f}s"
        else:
            t = f"{time_ms}ms"
        return t

    def print_result_details(self, result_details, result_list):
        test = self.retrieve_a_synthetic_test(result_details["testid"])
        for result in result_list:
            formatted_response_size = "{:.2f} MiB".format(result["metrics"]["response_size"][0][1]/ (1024 * 1024))
            status = "Successful" if result["metrics"]["status"][0][1] == 1 else "Failed"

            if result["testResultCommonProperties"]["id"] == result_details["resultid"]:
                print(self.fill_space("Name".upper(), 30), "Value".upper())
                print(self.fill_space("Result Id", 30), result_details["resultid"])
                print(self.fill_space("Start Time", 30), self.change_time_format(result["metrics"]["response_time"][0][0], False))
                print(self.fill_space("Status", 30), status)
                print(self.fill_space("Retries", 30), test[0]["configuration"]["retries"])
                print(self.fill_space("Response Time", 30), str(self.convert_milliseconds(result["metrics"]["response_time"][0][1])))
                if result_details["syntheticType"] == SSLCertificate_TYPE:
                    if status == "Successful":
                        if result["metrics"]["synthetic.customMetrics.valid"][0][1] == 1:
                            print(self.fill_space("Certificate is Valid", 30), "Yes")
                            print(self.fill_space("Days Remaining", 30), result["metrics"]["synthetic.customMetrics.daysRemaining"][0][1])
                            print(self.fill_space("Date of Issue", 30), self.change_time_format(result["metrics"]["synthetic.customMetrics.validFrom"][0][1], True))
                            print(self.fill_space("Date of Expiry", 30), self.change_time_format(result["metrics"]["synthetic.customMetrics.validTo"][0][1], True))
                        else:
                            print(self.fill_space("Certificate is Valid", 30), "No")
                else:
                    print(self.fill_space("Response Size", 30), str(formatted_response_size))
                    if "har" in result_details:
                        har_path = os.path.join(result_details["testid"], result_details["resultid"])
                        os.makedirs(har_path, exist_ok=True)
                        file_path = os.path.join(har_path, "HAR.json")
                        with open(file_path, 'w') as f:
                            json.dump(result_details['har'], f)
                        print(self.fill_space("HAR", 30), f"HAR has been saved to {file_path}")
                    else:
                        print(self.fill_space("HAR", 30), "N/A")
                    if "image" in result_details:
                        with open("images.tar", "wb") as f:
                            f.write(result_details["image"])
                        with tarfile.open("images.tar", "r") as tar:
                            images_path = os.path.join(result_details["testid"], result_details["resultid"], "Screenshots")
                            tar.extractall(path=images_path)
                        print(self.fill_space("Screenshots", 30), f"Screenshots has been saved to {images_path}")
                    else:
                        print(self.fill_space("Screenshots", 30), "N/A")
                    if "video" in result_details:
                        with open("videos.tar", "wb") as f:
                            f.write(result_details["video"])
                        with tarfile.open("videos.tar", "r") as tar:
                            videos_path = os.path.join(result_details["testid"], result_details["resultid"], "Recordings")
                            tar.extractall(path=videos_path)
                        print(self.fill_space("Recordings", 30), f"Recordings has been saved to {videos_path}")
                    else:
                        print(self.fill_space("Recordings", 30), "N/A")
                    if "sub" in result_details:
                        print("")
                        print(self.__fix_length("*", 80))
                        print("Subtransactions ")
                        print(self.__fix_length("*", 80))
                        for x in range(len(result_details["sub"])):
                            for key, value in result_details["sub"][x]["properties"].items():
                                if key == 'finishTime' or key == 'startTime':
                                    print(self.fill_space(key, 30), self.format_time(value))
                                else:
                                    print(self.fill_space(key, 30), value)
                            for key, value in result_details['sub'][x]["metrics"].items():
                                print(self.fill_space(key, 30), value)
                            print(self.__fix_length("*", 80))
                    else:
                        print(self.fill_space("Subtransactions", 30), "N/A")
                    if "logs" in result_details:
                        print("")
                        print("\nConsole logs ")
                        print(self.__fix_length("*", 80))
                        if "console.log" in result_details["logs"]:
                            print(result_details["logs"]["console.log"])
                        else:
                            print(result_details["logs"])
                        print(self.__fix_length("*", 80))
                        if result_details["syntheticType"] != HTTPScript_TYPE:
                            if "browser.json" in result_details["logs"]:
                                print("Browser logs")
                                print(self.__fix_length("*", 80))
                                browserlogs = json.loads(result_details["logs"]["browser.json"])
                                for logs in browserlogs:
                                        print(logs["level"]+ "\n" + self.change_time_format(logs["timestamp"], False) + "\n" +  logs["message"])
                                print("")
                                print(self.__fix_length("*", 80))
                            else:
                                print(self.fill_space("Browser Logs", 30), "N/A")
                if "errors" in result["testResultCommonProperties"]:
                    print("Error")
                    print(self.__fix_length("*", 80))
                    errors = result["testResultCommonProperties"]["errors"][0].split(",")
                    for e in errors:
                        print(e)
                else:
                    print(self.fill_space("Error", 30), "N/A")
                break
        else:
            print(f"no result \"{result_details['resultid']}\" found, ensure the window-size is correct.")

    def print_result_list(self, result_list):
        id_length = 38
        start_time_length = 30
        loc_length = 30
        status_length = 15
        response_size_length = 8
        response_time_length = 18
        sorted_result = self.__sort_test_result(result_list)

        print(self.fill_space("ID".upper(), id_length),
              self.fill_space("start Time".upper(), start_time_length),
              self.fill_space("Location".upper(), loc_length),
              self.fill_space("Status".upper(), status_length),
              self.fill_space("Response Time".upper(), response_time_length),
              self.fill_space("Response size".upper(), response_size_length))
        for result in sorted_result:
            formatted_response_size = "{:.2f} MiB".format(result["metrics"]["response_size"][0][1]/ (1024 * 1024))
            status = "Successful" if result["metrics"]["status"][0][1] == 1 else "Failed"

            print(self.fill_space(result["testResultCommonProperties"]["id"], id_length ),
                  self.fill_space(str(self.change_time_format(result["metrics"]["response_time"][0][0], False)), start_time_length),
                  self.fill_space(result["testResultCommonProperties"]["locationDisplayLabel"], loc_length),
                  self.fill_space(status, status_length),
                  self.fill_space(str(self.convert_milliseconds(result["metrics"]["response_time"][0][1])), response_time_length),
                  self.fill_space(str(formatted_response_size), response_size_length))

    def retrieve_synthetic_test_by_filter(self, tag_filter, page=1, page_size=200, window_size=60*60*1000):
        host = self.auth["host"]
        token = self.auth["token"]
        self.check_host_and_token(host, token)

        if isinstance(tag_filter[0], str) and tag_filter[0].lower() == "locationid":
            filter = "locationId"
        elif isinstance(tag_filter[0], str) and tag_filter[0].lower() == "applicationid":
            filter = "applicationId"
        else:
            self.exit_synctl(ERROR_CODE, f"Invalid filter : {tag_filter[0]}")

        test_list_url = f"{host}/api/synthetics/settings/tests?{filter}={tag_filter[1]}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"apiToken {token}"
        }
        try:
            retrieve_res = requests.get(test_list_url,
                                         headers=headers,
                                         timeout=60,
                                         verify=self.insecure)

            if _status_is_200(retrieve_res.status_code):
                data = retrieve_res.json()
                return data
            else:
                print('retrieve test failed, status code:',
                      retrieve_res.status_code)
                return None
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")


    def delete_a_synthetic_test(self, test_id=""):
        """delete a Synthetic by id"""
        # https://instana.github.io/openapi/#operation/deleteSyntheticTest
        self.check_host_and_token(self.auth["host"], self.auth["token"])
        if test_id == "":
            print("test id should not be empty")
            return

        host = self.auth["host"]

        # delete url
        delete_url = f"{host}/api/synthetics/settings/tests/{test_id}"
        headers = {
            'Content-Type': 'application/json',
            "Authorization": "apiToken %s" % (self.auth["token"])
        }
        try:
            del_result = requests.delete(delete_url,
                                         headers=headers,
                                         timeout=60,
                                         verify=self.insecure)

            if _status_is_204(del_result.status_code):
                print(f'test \"{test_id}\" deleted')
            elif _status_is_429(del_result.status_code):
                self.exit_synctl(ERROR_CODE, TOO_MANY_REQUEST_ERROR)
            else:
                print(
                    f"Fail to delete {test_id}, status code {del_result.status_code}")
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")

    def delete_multiple_synthetic_tests(self, tests_list: list):
        start_time = time.time()
        total_number = 0
        for t in tests_list:
            self.delete_a_synthetic_test(t)
            total_number += 1
        end_time = time.time()
        total_time = round((end_time-start_time)*1000, 3)
        print(f"total deleted: {total_number}, time used: {total_time}ms")

    def delete_tests_label_match_regex(self, label_regex=None):
        """delete all tests which match regex"""
        delete_syn_id_lists = []
        if label_regex is None:
            print('no regex')
        else:
            prog = re.compile(label_regex)

            # get full list of syn_tests
            full_syn_tests = self.retrieve_all_synthetic_tests()
            for syn in full_syn_tests:
                label_1 = syn["label"]
                match_result1 = prog.match(label_1)
                if match_result1 is not None:
                    print(f"test \"{label_1}\"")
                    # delete it
                    delete_syn_id_lists.append(syn["id"])
            print('total match:', len(delete_syn_id_lists))
            if len(delete_syn_id_lists) > 0 and self.ask_answer("are you sure to delete these tests?"):
                self.delete_multiple_synthetic_tests(delete_syn_id_lists)

    def delete_tests_match_location(self, match_location=None):
        """delete all tests match location"""
        delete_syn_id_lists = []
        if match_location is None:
            print("no location")
        else:
            # get full list of syn_tests
            full_syn_tests = self.retrieve_all_synthetic_tests()
            for syn in full_syn_tests:
                if syn is None:
                    continue
                label_1 = syn["label"]
                syn_locations = syn["locations"]
                if syn_locations is not None and len(syn_locations) == 1 and syn_locations[0] == match_location:
                    print(f"test \"{label_1}\"")
                    # add to delete list
                    delete_syn_id_lists.append(syn["id"])
            print(f'Total tests with location id \"{match_location}\":', len(
                delete_syn_id_lists))
            if len(delete_syn_id_lists) > 0 and self.ask_answer("are you sure to delete these tests?"):
                self.delete_multiple_synthetic_tests(delete_syn_id_lists)

    def delete_tests_without_location(self):
        """delete all tests without location"""
        delete_syn_id_lists = []
        # get full list of syn_tests
        full_syn_tests = self.retrieve_all_synthetic_tests()
        for syn in full_syn_tests:
            label_1 = syn["label"]
            syn_locations = syn["locations"]
            if len(syn_locations) == 0:
                print(f"test \"{label_1}\"")
                # delete it
                delete_syn_id_lists.append(syn["id"])
        if len(delete_syn_id_lists) > 0:
            print('Total tests:', len(delete_syn_id_lists))
        else:
            print('no tests match no locations')
        if len(delete_syn_id_lists) > 0 and self.ask_answer("are you sure to delete these tests?"):
            self.delete_multiple_synthetic_tests(delete_syn_id_lists)

    def __sort_synthetic_tests(self, syn_list):
        """sort Synthetic list by locationDisplayLabels"""
        new_list = sorted(
            syn_list, key=lambda syn: syn["locationDisplayLabels"] if syn is not None else [])
        return new_list

    def print_synthetic_test(self, out_list=None, test_id="", test_type="", output_terminal=False, summary_list=None):
        n_list = self.__sort_synthetic_tests(out_list)
        # n_list = out_list
        if n_list is not None:
            self.__output_tests_to_terminal(
                n_list, test_type=test_type, summary_list=summary_list)
        else:
            self.__output_tests_to_terminal(
                self.test_lists, test_type=test_type, summary_list=summary_list)

    def __get_max_label_length(self, syn_list, max_len=60):
        label_len = 0
        if syn_list is not None and isinstance(syn_list, list):
            for syn in syn_list:
                if syn is not None and label_len < len(syn["label"]):
                    label_len = len(syn["label"])
        if label_len > 60:
            return 60
        else:
            return label_len if label_len > 10 else 10

    def map_synthetic_type_label(self, syn_type):
        if syn_type == HTTPAction_TYPE:
            syn_type = "API Simple"
        elif syn_type == HTTPScript_TYPE:
            syn_type = "API Script"
        elif syn_type == WebpageAction_TYPE:
            syn_type = "Webpage Simple"
        elif syn_type == WebpageScript_TYPE:
            syn_type = "Webpage Script"
        elif syn_type == BrowserScript_TYPE:
            syn_type = "Browser Script"
        elif syn_type == SSLCertificate_TYPE:
            syn_type = "SSLCertificate"

        return syn_type

    def __output_tests_to_terminal(self, tests: list, test_type="", summary_list=None):
        id_length = 22
        max_label_length = self.__get_max_label_length(tests)
        syn_type_length = 15
        test_frequency_length = 10
        active_length = 6
        success_rate_length = 12
        response_time_length = 12
        location_str = NOT_APPLICABLE

        test_type = "" if test_type is None else test_type

        if summary_list is None:
            print(self.fill_space("ID".upper(), id_length),
                  self.fill_space("Label".upper(), max_label_length),
                  self.fill_space("syntheticType".upper(), syn_type_length),
                  self.fill_space("Frequency".upper(), test_frequency_length),
                  self.fill_space("Active".upper(), active_length),
                  self.fill_space("Locations".upper()),
                  "URL".upper())
            output_lists = []
            for t in tests:
                if t is None:
                    continue
                syn_type = t['configuration']['syntheticType']
                syn_type = self.map_synthetic_type_label(syn_type)

                current_type = t['configuration']['syntheticType']
                if current_type in (HTTPAction_TYPE, WebpageAction_TYPE, SSLCertificate_TYPE):
                    if len(t['locations']) > 0:
                        # locations,
                        location_str = ','.join(t['locationDisplayLabels'])
                    else:
                        location_str = NOT_APPLICABLE
                    if test_type == "" or (test_type != "" and current_type == test_type):
                        print(self.fill_space(t["id"], id_length),
                              self.fill_space(t['label'], max_label_length),
                              self.fill_space(syn_type, syn_type_length),
                              self.fill_space(self.format_frequency(t["testFrequency"]), test_frequency_length),
                              self.fill_space(str(t["active"]), active_length),
                              self.fill_space(location_str),
                              t['configuration']['url'] if 'url' in t['configuration'] else (
                                  t['configuration']['hostname'] if 'hostname' in  t['configuration'] else None))
                        output_lists.append(t)
                if t['configuration']['syntheticType'] in [HTTPScript_TYPE, WebpageScript_TYPE, BrowserScript_TYPE]:
                    if len(t['locations']) > 0:
                        location_str = ','.join(t['locationDisplayLabels'])
                    else:
                        location_str = NOT_APPLICABLE
                    if test_type == "" or (test_type != "" and current_type == test_type):
                        print(self.fill_space(t["id"], id_length),
                              self.fill_space(t['label'], max_label_length),
                              self.fill_space(syn_type, syn_type_length),
                              self.fill_space(self.format_frequency(t["testFrequency"]), test_frequency_length),
                              self.fill_space(str(t["active"]), active_length),
                              self.fill_space(location_str),
                              "N/A")  # None URL => N/A
                        output_lists.append(t)
        else:
            # show title
            print(self.fill_space("ID".upper(), id_length),
                  self.fill_space("Label".upper(), max_label_length),
                  self.fill_space("syntheticType".upper(), syn_type_length),
                  self.fill_space("Frequency".upper(), test_frequency_length),
                  self.fill_space("SuccessRate".upper(), success_rate_length),
                  self.fill_space("Latency".upper(), response_time_length),
                  self.fill_space("Active".upper(), active_length),
                  self.fill_space("Locations".upper()),
                  "URL".upper())
            # tests = self.test_lists
            output_lists = []
            for t in tests:
                if t is None:
                    continue
                success_rate_value = "No Data"
                current_response_time = "No Data"
                if t["id"] in summary_list:
                    success_rate_value = summary_list[t["id"]]["success_rate"]
                    # current_response_time = summary_list[""]
                    current_response_time = str(
                        summary_list[t["id"]]["response_time"])+"ms" if summary_list[t["id"]]["response_time"] != "N/A" else "N/A"
                # else:
                #     print(t["id"], "not in summary list")
                syn_type = t['configuration']['syntheticType']
                syn_type = self.map_synthetic_type_label(syn_type)

                current_type = t['configuration']['syntheticType']
                if current_type in (HTTPAction_TYPE, WebpageAction_TYPE, SSLCertificate_TYPE):
                    if len(t['locations']) > 0:
                        # locations,
                        location_str = ','.join(t['locationDisplayLabels'])
                    else:
                        location_str = NOT_APPLICABLE
                    if test_type == "" or (test_type != "" and current_type == test_type):
                        print(self.fill_space(t["id"], id_length),
                              self.fill_space(t['label'], max_label_length),
                              self.fill_space(syn_type, syn_type_length),
                              self.fill_space(self.format_frequency(t["testFrequency"]), test_frequency_length),
                              self.fill_space(str(success_rate_value),
                                              success_rate_length),
                              self.fill_space(current_response_time,
                                              response_time_length),
                              self.fill_space(str(t["active"]), active_length),
                              self.fill_space(location_str),
                              t['configuration']['url'] if 'url' in t['configuration'] else 'None')
                        output_lists.append(t)
                if (t['configuration']['syntheticType'] in [HTTPScript_TYPE, WebpageScript_TYPE, BrowserScript_TYPE]):
                    if len(t['locations']) > 0:
                        location_str = ','.join(t['locationDisplayLabels'])
                    else:
                        location_str = NOT_APPLICABLE
                    if test_type == "" or (test_type != "" and current_type == test_type):
                        print(self.fill_space(t["id"], id_length),
                              self.fill_space(t['label'], max_label_length),
                              self.fill_space(syn_type, syn_type_length),
                              self.fill_space(self.format_frequency(t["testFrequency"]), test_frequency_length),
                              self.fill_space(str(success_rate_value),
                                              success_rate_length),
                              self.fill_space(current_response_time,
                                              response_time_length),
                              self.fill_space(str(t["active"]), active_length),
                              self.fill_space(location_str),
                              "N/A")  # None URL => N/A
                        output_lists.append(t)
        print('total:', len(output_lists))

    def save_api_script_to_local(self, test):
        # save api script to local file
        if "script" in test["configuration"]:
            api_script = test["configuration"]["script"]
            if test["configuration"]["syntheticType"] == WebpageScript_TYPE:
                api_label = test["label"]+".side"
            else:
                api_label = test["label"]+".js"
            self.__save_script_to_local(api_script, label=api_label)

        # save bundle to zip file
        if "scripts" in test["configuration"]:
            bundle_script = test["configuration"]["scripts"]["bundle"]
            local_label = test["label"]+".zip"
            self.__save_bundle_to_zip(bundle_script, label=local_label)

    def __save_script_to_local(self, script, label="synthetic-script.js"):
        file_path = os.getcwd() + "/" + label
        if label.endswith('.side'):
            with open(file_path, "w", encoding="utf-8") as side_file:
                side_file.write(script)
        else:
            with open(file_path, "w", encoding="utf-8") as js_file:
                js_file.write(script)
        print(f"script is written to file {file_path}")

    def __save_bundle_to_zip(self, script, label="synthetic-bundle.zip"):
        """save bundle script to zip"""
        file_path = os.getcwd() + "/" + label
        with open(file_path, "wb") as zip_file:
            zip_file.write(b64decode(script))
        print(f"bundle script is written to file {file_path}")

    def print_a_synthetic_details(self, single_test, show_json=False, show_details=False, show_script=False):
        """output a single test details info"""
        if single_test is None or len(single_test) == 0:
            print("no Synthetic test")
            return
        # show title
        if show_json is True:
            # print json data
            print(json.dumps(single_test[0]))
        elif show_details is True:
            self.__print_a_synthetic_details(single_test)
        elif show_script is True:
            self.__print_a_synthetic_script(single_test[0])

    def __print_a_synthetic_details(self, single_test):
        """show a Synthetic test details data"""
        a_single_test = single_test[0]
        syn_label = a_single_test["label"]

        config_details = None
        print(self.fill_space("Name".upper(), 30), "Value".upper())
        for key, value in a_single_test.items():
            if key == "configuration":
                config_details = value
            else:
                if key == 'createdAt' or key == 'modifiedAt':
                    print(self.fill_space(key, 30), self.format_time(value))
                elif key =="testFrequency" and value > 60:
                    print(self.fill_space(key, 30), self.format_frequency(value))
                else:
                    print(self.fill_space(key, 30), value)

        print("---- CONFIGURATION ----")
        # show script content
        script_str = None
        for key, value in config_details.items():
            # api script
            if key == "script":
                script_str = value
            # print bundle script
            elif key == "scripts":
                for k1, v1 in value.items():
                    print(self.fill_space(k1, 30), v1)
            elif key == "syntheticType":
                syn_type = self.map_synthetic_type_label(value)
                print(self.fill_space(key, 30), syn_type)
            else:
                print(self.fill_space(key, 30), value)
        if script_str is not None:
            print("")
            print(self.__fix_length("*", 80))
            print("Test Script ")
            print(f"Label: {syn_label} ")
            print(self.__fix_length("*", 80))
            print(script_str)

    def __fix_length(self, print_str, length=60):
        if len(print_str) < length:
            return print_str+"*"*(length-len(print_str))
        else:
            return print_str

    def __is_httpaction(self, syn_test):
        if syn_test['configuration']['syntheticType'] == HTTPAction_TYPE:
            return True
        else:
            return False

    def __is_httpscript(self, syn_test):
        if syn_test['configuration']['syntheticType'] in [HTTPScript_TYPE, BrowserScript_TYPE, WebpageScript_TYPE]:
            return True
        else:
            return False

    def __print_a_synthetic_script(self, single_test):
        # show script content
        if self.__is_httpscript(single_test) is False:
            return
        if "script" in single_test["configuration"]:
            script_str = single_test["configuration"]["script"]
        else:
            script_str = ""  # bundle
            print("This is bundle script")
            return
        if script_str is not None and script_str != "":
            if single_test['configuration']['syntheticType'] == WebpageScript_TYPE:
                print(f"// Label: {single_test['label']}.side")
            else:
                print(f"// Label: {single_test['label']}.js")
            print(script_str)


class SmartAlert(Base):
    """create, query, update and delete Smart alerts"""

    def __init__(self) -> None:
        Base.__init__(self)

        self.payload = None
        self.alert_id = ""
        self.alert_lists = []

    def set_alert_id(self, alert_id):
        self.alert_id = alert_id

    def get_alert_id(self):
        return self.alert_id

    def set_alert_payload(self, payload=None):
        if payload is None:
            print("payload should not be none")
        else:
            self.payload = payload

    def get_alert_payload(self):
        return self.payload

    def retrieve_all_smart_alerts(self):
        self.check_host_and_token(self.auth["host"], self.auth["token"])
        host = self.auth["host"]
        token = self.auth["token"]

        retrieve_url = f"{host}/api/events/settings/global-alert-configs/synthetics/"

        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"apiToken {token}"
        }
        try:
            alert_result = requests.get(retrieve_url,
                                        headers=headers,
                                        timeout=60,
                                        verify=self.insecure)

            if _status_is_200(alert_result.status_code):
                data = alert_result.json()
                return data
            else:
                self.exit_synctl(ERROR_CODE, f'get alert failed, status code: {alert_result.status_code}')
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")

    def retrieve_a_smart_alert(self, alert_id=""):
        self.check_host_and_token(self.auth["host"], self.auth["token"])
        host = self.auth["host"]
        token = self.auth["token"]

        retrieve_url = f"{host}/api/events/settings/global-alert-configs/synthetics/{alert_id}"

        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"apiToken {token}"
        }
        try:
            alert_result = requests.get(retrieve_url,
                                        headers=headers,
                                        timeout=60,
                                        verify=self.insecure)

            if _status_is_200(alert_result.status_code):
                data = alert_result.json()

                if isinstance(data, list):
                    self.alert_lists = data
                    return data
                elif isinstance(data, dict):
                    self.alert_lists = [data]
                    return [data]
                else:
                    print('unknown data:', data)
            elif _status_is_404(alert_result.status_code):
                self.exit_synctl(ERROR_CODE,
                                 message=f'alert {alert_id} not found')
            else:
                self.exit_synctl(ERROR_CODE, f'get alert failed, status code: {alert_result.status_code}')
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")

    def retrieve_all_alerting_channel(self):
        self.check_host_and_token(self.auth["host"], self.auth["token"])
        host = self.auth["host"]
        token = self.auth["token"]

        retrieve_url = f"{host}/api/events/settings/alertingChannels/"

        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"apiToken {token}"
        }
        try:
            alert_channel_result = requests.get(retrieve_url,
                                                headers=headers,
                                                timeout=60,
                                                verify=self.insecure)

            if _status_is_200(alert_channel_result.status_code):
                data = alert_channel_result.json()
                return data
            else:
                self.exit_synctl(ERROR_CODE, f'get alert channel failed, status code: {alert_channel_result.status_code}')
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")

    def retrieve_a_single_alerting_channel(self, alert_channel):
        self.check_host_and_token(self.auth["host"], self.auth["token"])
        host = self.auth["host"]
        token = self.auth["token"]

        retrieve_url = f"{host}/api/events/settings/alertingChannels/{alert_channel}"

        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"apiToken {token}"
        }
        try:
            alert_channel_result = requests.get(retrieve_url,
                                                headers=headers,
                                                timeout=60,
                                                verify=self.insecure)

            if _status_is_200(alert_channel_result.status_code):
                data = alert_channel_result.json()
                return data
            else:
                self.exit_synctl(ERROR_CODE, f'get alert channel failed, status code: {alert_channel_result.status_code}')
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")
            self.exit_synctl(f"Connection to {host} timed out")


    def create_synthetic_alert(self):
        alert_payload = self.payload
        self.check_host_and_token(self.auth["host"], self.auth["token"])
        host = self.auth["host"]
        token = self.auth["token"]

        create_url = f"{host}/api/events/settings/global-alert-configs/synthetics"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"apiToken {token}"
        }
        try:
            create_res = requests.post(create_url,
                                       headers=headers,
                                       data=alert_payload,
                                       timeout=60,
                                       verify=self.insecure)

            if _status_is_200(create_res.status_code):
                # extracting data in json format
                data = create_res.json()
                alert_id = data["id"]
                alert_name = data["name"]
                print(f"smart alert \"{alert_name}\" created, id is \"{alert_id}\"")
            elif _status_is_429(create_res.status_code):
                self.exit_synctl(-1, TOO_MANY_REQUEST_ERROR)
            else:
                print('create test failed, status code:', create_res.status_code)
                if create_res.text:
                    print(create_res.text)
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")

    def invalid_create_options(self, invalid_options, items, tag_filter_type=None):
        for key, value in items:
            if key in invalid_options and value is not None:
                self.exit_synctl(ERROR_CODE, f"option: --{key} is not supported with tagFilterExpression type: {tag_filter_type}")

    def __delete_a_smart_alert(self, alert_id=""):
        """delete a smart alert"""
        if alert_id == "":
            print("alert id should not be empty")
            return
        self.check_host_and_token(self.auth["host"], self.auth["token"])
        host = self.auth["host"]

        delete_url = f"{host}/api/events/settings/global-alert-configs/synthetics/{alert_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "apiToken %s" % (self.auth["token"])
        }
        try:
            result = requests.delete(delete_url,
                                     headers=headers,
                                     timeout=60,
                                     verify=self.insecure)

            if _status_is_204(result.status_code):
                print(f'alert \"{alert_id}\" deleted')
            elif _status_is_404(result.status_code):
                self.exit_synctl(ERROR_CODE, f"{alert_id} not found")
            elif _status_is_429(result.status_code):
                self.exit_synctl(ERROR_CODE, TOO_MANY_REQUEST_ERROR)
            else:
                self.exit_synctl(ERROR_CODE, f"Failed to delete {alert_id}, status code {result.status_code}")
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")

    def delete_multiple_smart_alerts(self, alert_list):
        start_time = time.time()
        total_number = 0

        if alert_list is None or len(alert_list) == 0:
            print("No alerts to delete")
            return

        for alert in alert_list:
            self.__delete_a_smart_alert(alert)
            total_number += 1
        end_time = time.time()
        total_time = round((end_time-start_time)*1000, 3)
        print(
            f"total deleted: {total_number}, time used: {total_time}ms")

    def print_synthetic_alerts(self, alerts):
        id_length = 25
        max_label_length = 50
        severity_length = 10

        print(self.fill_space("ID".upper(), id_length),
              self.fill_space("label".upper(), max_label_length),
              self.fill_space("severity".upper(), severity_length),
              self.fill_space("Enabled".upper()),
              self.fill_space("Tests".upper()))

        for x in alerts:
            x["severity"] = {5: "WARNING", 10: "CRITICAL"}.get(x["severity"])
            if len(x["syntheticTestIds"]) > 0:
                test_str = ','.join(x['syntheticTestIds'])
            else:
                test_str = NOT_APPLICABLE
            print(self.fill_space(x["id"], id_length),
                  self.fill_space(x["name"], max_label_length),
                  self.fill_space((x["severity"]), severity_length),
                  self.fill_space(str(x["enabled"])),
                  self.fill_space(test_str))
        print('Total:', len(alerts))

    def print_a_alert_details(self, alert_id, single_alert, show_details=False, show_json=False):
        """Show a smart alert details data"""
        if single_alert is None or len(single_alert) == 0 or alert_id is None:
            print("no smart alert")
            return
        elif show_json is True:
            # print alert json
            print(json.dumps(single_alert[0]))
        elif show_details is True:
            self.__print_a_alert_details(single_alert)

    def __print_a_alert_details(self, single_alert):
        a_single_alert = single_alert[0]
        print(self.fill_space("Name".upper(), 30), "value".upper())
        for key, value in a_single_alert.items():
            if key == 'created' or key == 'initialCreated':
                print(self.fill_space(key, 30), self.format_time(value))
            elif key == 'severity':
                severity_mapping = {5 : "WARNING" , 10 : "CRITICAL" }
                print(self.fill_space(key, 30), severity_mapping.get(value))
            else:
                print(self.fill_space(key, 30), value)

    def print_alerting_channels(self, alert_channels):
        id_length = 50
        max_label_length = 55

        print(self.fill_space("ID".upper(), id_length),
              self.fill_space("label".upper(), max_label_length),
              self.fill_space("kind").upper())

        for channel in alert_channels:
            print(self.fill_space(channel["id"], id_length),
                  self.fill_space(channel["name"], max_label_length),
                  self.fill_space(channel["kind"]))


class UpdateSyntheticTest(SyntheticTest):

    def __init__(self) -> None:
        super().__init__()
        self.update_config = None
        self.test_id = ""

    def set_updated_payload(self, payload):
        if payload is None:
            print("payload should not be none")
        else:
            self.update_config = payload[0]

    def invalid_update_options(self, invalid_options, items, syn_type=None, toggle=None):
        for key, value in items:
            if key in invalid_options and value is not None:
                if toggle is not None:
                    self.exit_synctl(ERROR_CODE, f"option: --{key} is not allowed with --{toggle}")
                elif syn_type == SYN_TEST or syn_type == SYN_ALERT:
                    self.exit_synctl(ERROR_CODE, f"option: --{key} is not supported with {syn_type}s")

    def update_a_synthetic_test(self, test_id, new_payload):
        """API https://instana.github.io/openapi/#operation/updateSyntheticTest"""
        self.check_host_and_token(self.auth["host"], self.auth["token"])
        host = self.auth["host"]
        token = self.auth["token"]
        if new_payload is None:
            self.exit_synctl(ERROR_CODE, "config cannot be empty")

        if test_id is None or test_id == "":
            print("test id should not be empty")
            return
        else:
            put_url = f"{host}/api/synthetics/settings/tests/{test_id}"

        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"apiToken {token}"
        }
        try:
            update_result = requests.put(put_url,
                                         headers=headers,
                                         data=new_payload,
                                         timeout=60,
                                         verify=self.insecure)

            if _status_is_200(update_result.status_code):
                print(f"test {test_id} updated")
            elif _status_is_400(update_result.status_code):
                print(f'Error: {update_result}', update_result.content)
            elif _status_is_429(update_result.status_code):
                self.exit_synctl(ERROR_CODE, TOO_MANY_REQUEST_ERROR)
            else:
                print(
                    f'update test {test_id} failed, status code: {update_result.status_code}')
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")

    def update_using_file(self, file_name):
        with open(file_name, 'rb') as json_file:
            payload = json_file.read()
            return payload

    def update_label(self, label):
        """label"""
        if label is None or label == "":
            self.exit_synctl(ERROR_CODE, "no label")
        else:
            self.update_config["label"] = label

    def update_description(self, description):
        """description"""
        if description is None or description == "":
            self.exit_synctl(ERROR_CODE, "no description")
        else:
            self.update_config["description"] = description

    def update_record_video(self, record_video=False):
        if record_video is not None and record_video.upper() in ("TRUE", "FALSE"):
            self.update_config["configuration"]["recordVideo"] = record_video
        else:
            self.exit_synctl(ERROR_CODE, "record video should not be None")

    def update_browser(self, browser):
        if browser is not None and browser.upper() in ("CHROME", "FIREFOX"):
            self.update_config["configuration"]["browser"] = browser
        else:
            self.exit_synctl(ERROR_CODE, "browser should not be none")

    def update_active(self, active):
        """active"""
        if active is not None and active.upper() in ("TRUE", "FALSE"):
            self.update_config["active"] = active
        else:
            self.exit_synctl(ERROR_CODE, "active should not be none")

    def update_frequency(self, frequency):
        """update frequency [1,120], SSLCertificate test [1,1440]"""
        if 0 < frequency <= 120 :
            self.update_config["testFrequency"] = frequency
        elif self.update_config["configuration"]["syntheticType"] == SSLCertificate_TYPE and frequency <= 1440:
            self.update_config["testFrequency"] = frequency
        elif self.update_config["configuration"]["syntheticType"] == SSLCertificate_TYPE and frequency > 1440:
            self.exit_synctl(ERROR_CODE, "frequency is not valid, it should be in [1,1440]")
        else:
            self.exit_synctl(ERROR_CODE, "frequency is not valid, it should be in [1,120]")

    def update_locations(self, locations):
        """--locations update locations"""
        if locations is None:
            self.exit_synctl(ERROR_CODE, "no location")
        else:
            self.update_config["locations"] = locations

    def update_config_timeout(self, timeout):
        """--timeout 2m, <number>(ms|s|m)"""
        if timeout is None or timeout == "":
            self.exit_synctl(ERROR_CODE, "timeout should not be None")
        else:
            self.update_config["configuration"]["timeout"] = timeout

    def update_retries(self, retry: int):
        """retries"""
        if 0 <= retry <= 2:
            self.update_config["configuration"]["retries"] = retry
        else:
            self.exit_synctl(ERROR_CODE, "retry should be in [0, 2]")

    def update_retry_interval(self, interval: int):
        """retryInterval"""
        if 1 <= interval <= 10:
            self.update_config["configuration"]["retryInterval"] = interval
        else:
            self.exit_synctl(ERROR_CODE, "retryInterval should be in [1,10]")

    def update_ping_operation(self, method: str = "GET"):
        """operation"""
        valid_methods = ["GET", "HEAD", "POST", "PUT", "DELETE",
                         "CONNECT", "OPTIONS", "TRACE", "PATCH"]
        if method is not None and method.upper() in valid_methods:
            self.update_config["configuration"]["operation"] = method.upper()
        else:
            self.exit_synctl(ERROR_CODE, f"{method} is not allowed")

    def update_mark_synthetic_call(self, mark_synthetic_call):
        """mark Synthetic call"""
        mark_synthetic_call_options = ["true", "false"]
        if mark_synthetic_call is not None and mark_synthetic_call.lower() in mark_synthetic_call_options:
            self.update_config["configuration"]["markSyntheticCall"] = mark_synthetic_call
        else:
            self.exit_synctl(ERROR_CODE, "markSyntheticCall should be true or false")

    def update_config_script_file(self, script_file_name):
        """--script update script from a file"""
        try:
            with open(script_file_name, "r", encoding="utf-8") as file1:
                script = file1.read()
                if script is not None:
                    self.update_config["configuration"]["script"] = script
                else:
                    self.exit_synctl(ERROR_CODE, "script cannot be none")
        except FileNotFoundError as not_found_e:
            self.exit_synctl(ERROR_CODE, not_found_e)

    def update_bundle_entry_file(self, entry_file_name):
        if entry_file_name == "" or entry_file_name is None:
            self.exit_synctl(ERROR_CODE, "script file should not be None")
        else:
            self.update_config["configuration"]["scripts"]["scriptFile"] = entry_file_name

    def update_url(self, url):
        """update url"""
        if url is not None:
            self.update_config["configuration"]["url"] = url
        else:
            self.exit_synctl(ERROR_CODE, "url should not be none")

    def update_follow_redirect(self, follow_redirect):
        """update follow-redirect"""
        follow_redirect_options = ["True", "true", "False", "false"]
        if follow_redirect is not None and follow_redirect in follow_redirect_options:
            self.update_config["configuration"]["followRedirect"] = follow_redirect
        else:
            self.exit_synctl(ERROR_CODE, "followRedirect should be true/false ")

    def update_application_id(self, app_id):
        """update application id"""
        if app_id is not None:
            self.update_config["applicationId"] = app_id
        else:
            self.exit_synctl(ERROR_CODE, "application id should not be none")

    def update_websites(self, website):
        """update websites"""
        if website is not None:
            self.update_config["websites"] = website
        else:
            self.exit_synctl(ERROR_CODE, "application id should not be none")

    def update_mobile_app(self, mobile_app):
        """update mobile applications"""
        if mobile_app is not None:
            self.update_config["mobileApps"] = mobile_app
        else:
            self.exit_synctl(ERROR_CODE, "application id should not be none")

    def update_expect_status(self, expect_status):
        """update expect status"""
        if expect_status is not None:
            self.update_config["configuration"]["expectStatus"] = expect_status
        else:
            self.exit_synctl(ERROR_CODE, "expectStatus should not be none")

    def update_expect_json(self, expect_json):
        """update expect json"""
        if expect_json is not None:
            self.update_config["configuration"]["expectJson"] = json.loads(expect_json)
        else:
            self.exit_synctl(ERROR_CODE, "expectJson should not be none")

    def update_expect_not_empty(self, expect_not_empty):
        """update expect not empty"""
        if expect_not_empty is not None:
            self.update_config["configuration"]["expectNotEmpty"] = json.loads(expect_not_empty)
        else:
            self.exit_synctl(ERROR_CODE, "expectNotEmpty should not be none")

    def update_expect_exists(self, expect_exists):
        """update expect exists"""
        if expect_exists is not None:
            self.update_config["configuration"]["expectExists"] = json.loads(expect_exists)
        else:
            self.exit_synctl(ERROR_CODE, "expectExists should not be none")

    def update_allow_insecure(self, allow_insecure):
        """update allowInsecure"""
        allow_insecure_opions = ["true", "false"]
        if allow_insecure is not None and allow_insecure.lower() in allow_insecure_opions:
            self.update_config["configuration"]["allowInsecure"] = allow_insecure
        else:
            self.exit_synctl(ERROR_CODE, "allowInsecure should not be none")

    def update_expect_match(self, expect_match):
        """update expectMatch"""
        if expect_match is not None:
            self.update_config["configuration"]["expectMatch"] = expect_match
        else:
            self.exit_synctl(ERROR_CODE, "expectMatch should not be none")

    def update_validation_string(self, validation_string):
        """update validation string"""
        if validation_string is None or validation_string == "":
            self.exit_synctl(ERROR_CODE, "validation string should not be none")
        else:
            self.update_config["configuration"]["validationString"] = validation_string

    def update_bundle(self, bundle):
        """update bundle"""
        if bundle.endswith('.zip'):
            with open(bundle, 'rb') as file1:
                zip_content_byte = file1.read()
                zip_content_byte_base64 = b64encode(zip_content_byte)
                self.update_config["configuration"]["scripts"]["bundle"] = zip_content_byte_base64.decode(
                    'utf-8')
        else:
            self.update_config["configuration"]["scripts"]["bundle"] = bundle

    def update_custom_properties(self, custom_property):
        """update custom properties"""
        if any(s == '' or s.isspace() for s in custom_property):
            self.exit_synctl(ERROR_CODE, "Custom property should be <key>=<value>")

        for item in custom_property:
            key, value = item.split('=')
            if key == '' or value == '':
                self.exit_synctl(ERROR_CODE, "Custom property should be <key>=<value>")
            self.update_config["customProperties"][key] = value

    def update_body(self, body):
        """update body"""
        if body is None or body == "":
            self.exit_synctl(ERROR_CODE, "no body")
        else:
            self.update_config["configuration"]["body"] = body

    def update_headers(self, headers):
        """update headers"""
        if any(s == '' or s.isspace() for s in headers):
            self.exit_synctl(ERROR_CODE, "Headers should be <header>=<value>")

        for item in headers:
            key, value = item.split('=')
            if key == '' or value == '':
                self.exit_synctl(ERROR_CODE, "Headers should be <header>=<value>")
            self.update_config["configuration"]["headers"][key] = value

    def update_host(self, host):
        """update host for SSL test"""
        if host is not None:
            self.update_config["configuration"]["hostname"] = host
        else:
            self.exit_synctl(ERROR_CODE, "host should not be none")

    def update_port(self, port):
        """update port for SSL test"""
        if port is not None:
            self.update_config["configuration"]["port"] = port
        else:
            self.exit_synctl(ERROR_CODE, "port should not be none")

    def update_remaining_days(self, rem_days):
        if rem_days is not None:
            self.update_config["configuration"]["daysRemainingCheck"] = rem_days
        else:
            self.exit_synctl(ERROR_CODE, "remaining days should not be none")

    def get_updated_test_config(self):
        """return payload as json"""
        result = json.dumps(self.update_config)
        return result


class UpdateSmartAlert(SmartAlert):
    def __init__(self) -> None:
        super().__init__()
        self.update_config = None

    def set_updated_payload(self, payload):
        if payload is None:
            print("payload should not be none")
        else:
            self.update_config = payload[0]

    def update_using_file(self, file):
        with open(file, 'rb') as json_file:
            payload = json_file.read()
            return payload

    def update_description(self, description):
        """description"""
        if description is None or description == "":
            self.exit_synctl(ERROR_CODE, "no description")
        else:
            self.update_config["description"] = description

    def update_a_smart_alert(self, alert_id, new_payload):
        """API https://instana.github.io/openapi/#operation/updateSyntheticAlertConfig"""
        self.check_host_and_token(self.auth["host"], self.auth["token"])
        host = self.auth["host"]
        token = self.auth["token"]
        if new_payload is None:
            self.exit_synctl(ERROR_CODE, "config cannot be empty")

        if alert_id is None or alert_id == "":
            self.exit_synctl(ERROR_CODE, "alert id should not be none")
        else:
            update_url = f"{host}/api/events/settings/global-alert-configs/synthetics/{alert_id}"

        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"apiToken {token}"
        }
        try:
            update_result = requests.post(update_url,
                                          headers=headers,
                                          data=new_payload,
                                          timeout=60,
                                          verify=self.insecure)

            if _status_is_200(update_result.status_code):
                print(f"alert {alert_id} updated")
            elif _status_is_204(update_result.status_code):
                print(f"alert {alert_id} did not change")
            elif _status_is_400(update_result.status_code):
                print(f'Error: {update_result}', update_result.content)
            elif _status_is_429(update_result.status_code):
                self.exit_synctl(ERROR_CODE, TOO_MANY_REQUEST_ERROR)
            else:
                print(
                    f'update alert {alert_id} failed, status code: {update_result.status_code}, {update_result.text}')
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")

    def toggle_smart_alert(self, alert_id, toggle):
        """API https://instana.github.io/openapi/#operation/enableSyntheticAlertConfig
               https://instana.github.io/openapi/#operation/disableSyntheticAlertConfig"""

        self.check_host_and_token(self.auth["host"], self.auth["token"])
        host = self.auth["host"]
        token = self.auth["token"]

        if alert_id is None:
            self.exit_synctl(ERROR_CODE, "alert id should not be none")
        else:
            if toggle in ('enable', 'disable'):
                put_url = f"{host}/api/events/settings/global-alert-configs/synthetics/{alert_id}/{toggle}"

        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"apiToken {token}"
        }
        try:
            update_result = requests.put(put_url,
                                         headers=headers,
                                         timeout=60,
                                         verify=self.insecure)

            if _status_is_204(update_result.status_code):
                print(f"alert {alert_id} {toggle}d")
            elif _status_is_400(update_result.status_code):
                print(f'Error: {update_result}', update_result.content)
            elif _status_is_429(update_result.status_code):
                self.exit_synctl(ERROR_CODE, TOO_MANY_REQUEST_ERROR)
            else:
                print(
                    f'update alert {alert_id} failed, status code: {update_result.status_code}, {update_result.text}')
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")

    def update_alert_name(self, name):
        """update alert name"""
        if name == "" or name is None:
            self.exit_synctl(ERROR_CODE, "name should not be none")
        else:
            self.update_config["name"] = name

    def update_alert_severity(self, severity):
        """update severity"""
        severity_mapping = {"WARNING" : 5, "CRITICAL" :  10}
        if severity.upper() in ["WARNING", "CRITICAL"]:
            self.update_config["severity"] = severity_mapping.get(severity.upper())
        else:
            self.exit_synctl(ERROR_CODE, "severity should be warning or critical")

    def update_alert_channel(self, alert_channel):
        """update alerting channels"""
        if alert_channel is None or alert_channel == "":
            self.exit_synctl(ERROR_CODE, "alert channels should not be none")
        else:
            self.update_config["alertChannelIds"] = alert_channel

    def update_tests(self, synthetic_tests):
        """update synthetic tests"""
        if any(s == '' or s.isspace() for s in synthetic_tests):
            self.exit_synctl(ERROR_CODE, "synthetic tests should not be none")
        else:
            self.update_config["syntheticTestIds"] = synthetic_tests

    def update_violation_count(self, violation_count):
        """update violation count"""
        if violation_count is None:
            self.exit_synctl(ERROR_CODE, "violation count should not be none")
        elif violation_count >= 1 and violation_count <= 12:
            self.update_config["timeThreshold"]["violationsCount"] = violation_count
        else:
            self.exit_synctl(ERROR_CODE, "violation count should be in [1,12]")

    def update_tag_filter_expression(self, tag_filter_json):
        """update tag filter expression"""
        if tag_filter_json is not None:
            self.update_config["tagFilterExpression"] = tag_filter_json
        else:
            self.exit_synctl(ERROR_CODE, "Tag-filter expression should not be None")

    def get_updated_alert_config(self):
        """return payload as json"""
        result = json.dumps(self.update_config)
        return result


class PatchSyntheticTest(SyntheticTest):
    """patch Synthetic test"""

    def __init__(self) -> None:
        super().__init__()
        self.test_id = ""

    def __ensure_test_id_not_none(self, test_id):
        if test_id is None or test_id == "":
            self.exit_synctl(ERROR_CODE, "Patch Error: test id is None")

    def __patch_a_synthetic_test(self, test_id, data):
        self.check_host_and_token(self.auth["host"], self.auth["token"])
        host = self.auth["host"]
        token = self.auth["token"]

        self.__ensure_test_id_not_none(test_id)
        patch_url = f"{host}/api/synthetics/settings/tests/{test_id}"

        if data is None:
            self.exit_synctl(ERROR_CODE, "Patch Error:data cannot be empty")

        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"apiToken {token}"
        }
        try:
            patch_result = requests.patch(patch_url,
                                          headers=headers,
                                          data=data,
                                          timeout=60,
                                          verify=self.insecure)

            if _status_is_200(patch_result.status_code):
                print(f"{test_id} updated")
            elif _status_is_400(patch_result.status_code):
                print(f'Patch Error: {patch_result}', patch_result.json())
            elif _status_is_429(patch_result.status_code):
                print(TOO_MANY_REQUEST_ERROR)
            else:
                print(
                    f'patch test {test_id} failed, status code: {patch_result.status_code}')
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")

    def set_test_id(self, test_id):
        """set test id"""
        self.__ensure_test_id_not_none(test_id)
        self.test_id = test_id

    def patch_label(self, label):
        """label"""
        payload = {"label": ""}
        if label is None:
            print("no label")
        else:
            payload["label"] = label
            self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))

    def patch_description(self, description):
        """description"""
        payload = {"description": ""}
        if description is None:
            print("no description")
        else:
            payload["description"] = description
            self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))

    def patch_record_video(self, record_video=False):
        payload = {"configuration": {"recordVideo": False}}
        if record_video is not None and record_video.upper() in ("TRUE", "FALSE"):
            payload["configuration"]["recordVideo"] = record_video
            self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))

    def patch_browser(self, browser):
        payload = {"configuration": {"browser": "chrome"}}
        if browser is not None:
            payload["configuration"]["browser"] = browser
            self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))

    def patch_active(self, active):
        """active"""
        if active is None:
            return
        payload = {"active": False}
        if active == "false":
            payload["active"] = False
        if active == "true":
            payload["active"] = True
        self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))

    def patch_frequency(self, frequency):
        """patch frequency [1,120], SSLCertificate test [1,1440]"""
        test_payload = self.retrieve_a_synthetic_test(self.test_id)
        synthetic_type = test_payload[0]["configuration"]["syntheticType"]
        if synthetic_type == SSLCertificate_TYPE:
            payload = {"testFrequency": 1440}
        else:
            payload = {"testFrequency": 15}
        if frequency is None:
            frequency = 1440 if synthetic_type == SSLCertificate_TYPE else 15
        if frequency > 0 and frequency <= 120:
            payload["testFrequency"] = frequency
        elif synthetic_type == SSLCertificate_TYPE and frequency <= 1440:
            payload["testFrequency"] = frequency
        elif synthetic_type == SSLCertificate_TYPE and frequency > 1440:
            self.exit_synctl(ERROR_CODE, "frequency is not valid, it should be in [1,1440]")
        else:
            self.exit_synctl(ERROR_CODE, "frequency is not valid, it should be in [1,120]")
        self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))

    def patch_locations(self, locations):
        """--locations patch locations"""
        payload = {"locations": []}
        if locations is None:
            print("no location")
            return
        else:
            payload["locations"] = locations
            self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))

    def patch_config_timeout(self, timeout):
        """--timeout 2m, <number>(ms|s|m)"""
        payload = {"configuration": {"timeout": ""}}
        if timeout is None:
            return
        else:
            payload["configuration"]["timeout"] = timeout
        self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))

    def patch_retries(self, retry: int):
        """retries"""
        payload = {"configuration": {"retries": 0}}
        if retry >= 0 and retry <= 2:
            payload["configuration"]["retries"] = retry
        else:
            print("retry should be in [0, 2]")
            return
        self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))

    def patch_retry_interval(self, interval: int):
        """retryInterval"""
        payload = {"configuration": {"retryInterval": 1}}
        if interval is None:
            interval = 1
        if interval >= 1 and interval <= 10:
            payload["configuration"]["retryInterval"] = interval
        else:
            print("retryInterval should be in [1,10]")
            return
        self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))

    def patch_ping_operation(self, method: str = "GET"):
        """operation"""
        valid_methods = ["GET", "HEAD", "POST", "PUT", "DELETE",
                         "CONNECT", "OPTIONS", "TRACE", "PATCH"]
        payload = {"configuration": {"operation": ""}}
        if method is not None and method.upper() in valid_methods:
            payload["configuration"]["operation"] = method.upper()
            self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))
        else:
            print(f"{method} is not allowed")
            return

    def patch_mark_synthetic_call(self, markSyntheticCall):
        """mark Synthetic call"""
        markSyntheticCall_options = ["true", "false"]
        payload = {"configuration": {"markSyntheticCall": ""}}
        if markSyntheticCall is not None and markSyntheticCall.lower() in markSyntheticCall_options:
            payload["configuration"]["markSyntheticCall"] = markSyntheticCall
            self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))
        else:
            print("markSyntheticCall should be true or false")

    def __patch_script(self, script):
        """update script content"""
        payload = {"configuration": {"script": ""}}
        if script is not None:
            payload["configuration"]["script"] = script
            self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))
        else:
            print("script cannot be none")
            return

    def patch_script_from_file(self, script_file_name):
        """Patch API/Browser Script from a file"""
        try:
            with open(script_file_name, "r", encoding="utf-8") as file1:
                script_str = file1.read()
                self.__patch_script(script_str)
        except FileNotFoundError as not_found_e:
            print(ERROR_CODE, not_found_e)

    def patch_bundle(self, test_id, bundle):
        """update bundle"""
        test_result = self.retrieve_a_synthetic_test(test_id)
        try:
            bundle_entry_file = test_result[0]["configuration"]["scripts"]["scriptFile"]
            payload = {
                "configuration":
                    {
                        "syntheticType": "HTTPScript",
                        "scripts": {
                            "bundle": "",  # required
                            "scriptFile": bundle_entry_file  # required
                        }
                    }
            }
            if bundle.endswith('.zip'):
                with open(bundle, 'rb') as file1:
                    zip_content_byte = file1.read()
                    zip_content_byte_base64 = b64encode(zip_content_byte)
                    payload["configuration"]["scripts"]["bundle"] = zip_content_byte_base64.decode(
                        'utf-8')
            else:
                payload["configuration"]["scripts"]["bundle"] = bundle
            self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))
        except Exception as e:
            print(f"Error: Test {test_id} not found, exception {e}")

    def patch_bundle_entry_file(self, script_file, test_id):
        test_result = self.retrieve_a_synthetic_test(test_id)
        try:
            test_bundle = test_result[0]["configuration"]["scripts"]["bundle"]
            payload = {
                "configuration":
                    {
                        "syntheticType": "HTTPScript",
                        "scripts": {
                            "bundle": test_bundle,  # required
                            "scriptFile": ""  # required
                        }
                    }
            }
            if script_file == "" or script_file is None:
                print("script_file should not be None")
            else:
                payload["configuration"]["scripts"]["scriptFile"] = script_file
                self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))
        except:
            print(f"Error: Test {test_id} not found")

    def patch_url(self, url):
        """update url"""
        payload = {"configuration": {"url": ""}}
        if url is not None:
            payload["configuration"]["url"] = url
            self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))
        else:
            print("url should not be none")

    def patch_follow_redirect(self, follow_redirect):
        """update follow-redirect"""
        follow_redirect_options = ["True", "true", "False", "false"]
        payload = {"configuration": {"followRedirect": ""}}
        if follow_redirect is not None and follow_redirect in follow_redirect_options:
            payload["configuration"]["followRedirect"] = follow_redirect
            self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))
        else:
            print("followRedirect should be true/false ")

    def patch_expect_status(self, expect_status):
        """update expect status"""
        payload = {"configuration": {"expectStatus": ""}}
        if expect_status is not None:
            payload["configuration"]["expectStatus"] = expect_status
            self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))
        else:
            print("expectStatus should not be none")

    def patch_allow_insecure(self, allow_insecure):
        """update allow insecure"""
        allow_insecure_opions = ["true", "false"]
        payload = {"configuration": {"allowInsecure": ""}}
        if allow_insecure is not None and allow_insecure.lower() in allow_insecure_opions:
            payload["configuration"]["allowInsecure"] = allow_insecure
            self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))
        else:
            print("allowInsecure should be true/false")

    def patch_expect_json(self, expect_json):
        """update expect json"""
        payload = {"configuration": {"expectJson": ""}}
        if expect_json is not None:
            payload["configuration"]["expectJson"] = json.loads(expect_json)
            self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))
        else:
            print("expectJson should not be none")

    def patch_expect_not_empty(self, expect_not_empty):
        """update expect not empty"""
        payload = {"configuration": {"expectNotEmpty": ""}}
        if expect_not_empty is not None:
            payload["configuration"]["expectNotEmpty"] = json.loads(expect_not_empty)
            self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))
        else:
            print("expectNotEmpty should not be none")

    def patch_expect_exists(self, expect_exists):
        """update expect status"""
        payload = {"configuration": {"expectExists": ""}}
        if expect_exists is not None:
            payload["configuration"]["expectExists"] = json.loads(expect_exists)
            self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))
        else:
            print("expectExists should not be none")

    def patch_expect_match(self, expect_match):
        """update expect status"""
        payload = {"configuration": {"expectMatch": ""}}
        if expect_match is not None:
            payload["configuration"]["expectMatch"] = expect_match
            self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))
        else:
            print("expectMatch should not be none")

    def patch_validation_string(self, validation_string):
        """update validation string"""
        payload = {"configuration": {"validationString": ""}}
        if validation_string is None or validation_string == "":
            print("validation string should not be none")
        else:
            payload["configuration"]["validationString"] = validation_string
            self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))


    def patch_custom_properties(self, test_id, custom_property):
        """update custom properties"""
        test_result = self.retrieve_a_synthetic_test(test_id)
        payload = test_result[0]
        if any(s == '' or s.isspace() for s in custom_property):
            self.exit_synctl(ERROR_CODE, "Custom property should be <key>=<value>")

        for item in custom_property:
            key, value = item.split('=')
            if key == '' or value == '':
                self.exit_synctl(ERROR_CODE, "Custom property should be <key>=<value>")

            payload["customProperties"][key] = value
        self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))

    def patch_host(self, test_id, host):
        """update host for SSL test"""
        payload = {"configuration": {"hostname": ""}}
        if host is not None:
            payload["configuration"]["hostname"] = host
            self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))
        else:
            print("host should not be none")

    def patch_port(self, test_id, port):
        """update port for SSL test"""
        payload = {"configuration": {"port": ""}}
        if port is not None:
            payload["configuration"]["port"] = port
            self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))
        else:
            print("port should not be none")

    def patch_remaining_days(self, test_id, rem_days):
        payload = {"configuration": {"daysRemainingCheck": ""}}
        if rem_days is not None:
            payload["configuration"]["daysRemainingCheck"] = rem_days
            self.__patch_a_synthetic_test(self.test_id, json.dumps(payload))
        else:
            print("remaining days should not be none")


class SyntheticResult(Base):

    def __init__(self) -> None:
        super().__init__()
        self.default_page_size = 200

    def __parse_window_size_num(self, num: str):
        match1 = re.match(r"(^[1-9]+[0-9]*)", num)
        if match1 is not None:
            return int(match1.group())
        else:
            self.exit_synctl(ERROR_CODE, f"{num} is not correct, use <num>m, <num>h")

    def get_window_size(self, window_size: str):
        re_min = re.compile("^[1-9]+[0-9]*m$")
        min_full_match = re_min.fullmatch(window_size)

        re_hour = re.compile("^[1-9]+[0-9]*h$")
        hour_full_match = re_hour.fullmatch(window_size)
        if min_full_match is not None:
            minutes = self.__parse_window_size_num(window_size)
            if minutes > 0 and minutes <= 60:
                return minutes * 60 * 1000
            else:
                print("minutes should be in [1, 60]")
        elif hour_full_match is not None:
            hours = self.__parse_window_size_num(window_size)
            if hours > 0 and hours <= 24:
                return hours * 60 * 60 * 1000
            else:
                print("hours should be in [1, 24]")
        else:
            self.exit_synctl(ERROR_CODE, f"{window_size} for --window-size is not supported")

        # got an error when retrieve test summary list failed, status code: 400
        # {"code":400,"message":"'synthetic.metricsStatus' metric: the granularity in relation to the windowSize provides too many values"}
        # remove days support temporarily
        # re_day = re.compile("^[1-9]+[0-9]*d$")
        # day_full_match = re_day.fullmatch(window_size)
        # if day_full_match is not None:
        #     days = self.__parse_window_size_num(window_size)
        #     if days > 0 and days <= 7:
        #         return days * 24 * 60 * 60 * 1000
        #     else:
        #         print("days should be in [1, 7]")

    def __get_test_summary_list(self, page=1, test_id=None, page_size=200, window_size=60*60*1000):
        # https://instana.github.io/openapi/#section/Get-Synthetic-test-playback-results
        # curl --request POST 'http://{host}/api/synthetics/results/testsummarylist' \
        #  --header "Authorization: apiToken <YourToken>" -i \
        #  --header "Content-Type: application/json" \
        #  -d '{
        #      "syntheticMetrics":["synthetic.metricsStatus"],
        #      "metrics": [
        #       {
        #          "aggregation": "SUM",
        #          "granularity": 60,
        #          "metric": "synthetic.metricsStatus"
        #       }],
        #       "timeFrame": {
        #         "to": 0,
        #         "windowSize": 3600000
        #      }
        # }'
        # granularity
        #     If it is not set you will get an aggregated value for the selected timeframe
        #     If the granularity is set you will get data points with the specified granularity in seconds
        #     The granularity should not be greater than the windowSize (important: windowSize is expressed in milliseconds)
        #     The granularity should not be set too small relative to the windowSize to avoid creating an excessively large number of data points (max 600)
        #     The granularity values are the same for all metrics
        self.check_host_and_token(self.auth["host"], self.auth["token"])
        host = self.auth["host"]
        token = self.auth["token"]

        summary_config = {
            "syntheticMetrics": ["synthetic.metricsStatus", "synthetic.metricsResponseTime"],
            "metrics": [{
                "aggregation": "SUM",
                "granularity": 600,
                "metric": "synthetic.metricsStatus"
            }, {
                "aggregation": "MEAN",
                "granularity": 600,  # granularity max 600
                "metric": "synthetic.metricsResponseTime"
            }],
            "timeFrame": {
                "to": 0,
                "windowSize": window_size
            },
            "pagination": {
                "page": page,
                "pageSize": page_size
            }
        }

        if test_id is not None and len(test_id) > 0:
            summary_config["tagFilters"] = [{
                "stringValue": test_id,
                "name": "synthetic.testId",
                "operator": "EQUALS"
            }]

        test_summary_list_url = f"{host}/api/synthetics/results/testsummarylist"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"apiToken {token}"
        }
        try:
            summary_res = requests.post(test_summary_list_url,
                                        headers=headers,
                                        data=json.dumps(summary_config),
                                        timeout=60,
                                        verify=self.insecure)

            if _status_is_200(summary_res.status_code):
                # extracting data in json format
                data = summary_res.json()
                return data
            elif _status_is_400(summary_res.status_code):
                print(f'Bad Request: status code: {summary_res.status_code}')
                if summary_res.text:
                    print("Error Message:", summary_res.text)
                self.exit_synctl(error_code=ERROR_CODE)
            elif _status_is_429(summary_res.status_code):
                self.exit_synctl(ERROR_CODE, TOO_MANY_REQUEST_ERROR)
            else:
                print('retrieve test summary list failed, status code:',
                      summary_res.status_code)
                if summary_res.text:
                    print("Error Message:", summary_res.text)
                self.exit_synctl(ERROR_CODE)
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")

    def convert_summary_list_dict(self, summary_result, metrics_summary):
        if summary_result is None or not isinstance(summary_result, dict):
            return
        for item in summary_result["items"]:
            metrics_summary[item["testResultCommonProperties"]["testId"]] = {
                "success_rate": "N/A",  # default N/A
                "response_time": "N/A"  # default N/A
            }
            total_test_runs, successful_test_runs, response_time = None, None, None
            if "total_test_runs" in item["metrics"]:
                total_test_runs = item["metrics"]["total_test_runs"][0][1]
            if "successful_test_runs" in item["metrics"]:
                successful_test_runs = item["metrics"]["successful_test_runs"][0][1]
            if "response_time" in item["metrics"]:
                response_time = item["metrics"]["response_time"][0][1]

            if total_test_runs is not None and successful_test_runs is not None:
                metrics_summary[item["testResultCommonProperties"]["testId"]]["success_rate"] = str(
                    f"{successful_test_runs}/{total_test_runs}")

            if response_time is not None:
                metrics_summary[item["testResultCommonProperties"]["testId"]
                ]["response_time"] = str(round(response_time, 2))

    def get_summary_list(self, window_size, test_id=None):
        """convert summary list to a dict"""
        metrics_summary = {}
        window_size_ms = self.get_window_size(window_size)
        summary_result = self.__get_test_summary_list(page=1,
                                                      page_size=self.default_page_size,
                                                      window_size=window_size_ms,
                                                      test_id=test_id)
        self.convert_summary_list_dict(summary_result, metrics_summary)

        page = summary_result["page"] if "page" in summary_result else 1
        page_size = summary_result["pageSize"] if "pageSize" in summary_result else 200
        if "totalHits" in summary_result:
            total_hits = summary_result["totalHits"]

        if page_size >= total_hits:
            return metrics_summary
        else:
            total_pages = total_hits/page_size
            if (total_pages - round(total_pages)) > 0:
                total_pages += 1
            for x in range(1, round(total_pages)):
                summary_result = self.__get_test_summary_list(page=x+1,
                                                              page_size=self.default_page_size,
                                                              window_size=window_size_ms,
                                                              test_id=test_id)
                self.convert_summary_list_dict(summary_result, metrics_summary)
            return metrics_summary


class Application(Base):

    def __init__(self) -> None:
        super().__init__()
        self.default_page_size = 200
        self.name_filter = None
        self.to = 0
        self.window_size = 60*60*1000

    def set_name_filter(self, name_filter):
        if name_filter is not None:
            self.name_filter = name_filter

    def set_to(self, to):
        if to > 0:
            self.to = to

    def set_window_size(self, window_size):
        if window_size > 0:
            self.window_size = window_size

    def __get_application_list(self,
                               name_filter=None,
                               to=0,
                               page=1,
                               page_size=200,
                               window_size=60*60*1000,
                               application_boundary_scope=None):
        # API link https://instana.github.io/openapi/#operation/getApplications
        # curl --request GET 'https://<host>/api/application-monitoring/applications?nameFilter=<app-name>' \
        # --header "Authorization: apiToken <YourToken>" \
        # --header "Content-Type: application/json"
        self.check_host_and_token(self.auth["host"], self.auth["token"])
        host = self.auth["host"]
        token = self.auth["token"]

        application_list_url = f"{host}/api/application-monitoring/applications"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"apiToken {token}"
        }

        params_list = {
            # "nameFilter": "",  # Name of application
            "windowSize": window_size,  # Size of time window in milliseconds
            "to": to,  # Timestamp since Unix Epoch in milliseconds of the end of the time window
            "page": page,  # Page number from results
            "pageSize": self.default_page_size,  # Number of items per page
            "applicationBoundaryScope": "ALL"  # Enum: "ALL" "INBOUND"
        }
        if self.name_filter is not None:
            params_list["nameFilter"] = self.name_filter
        if application_boundary_scope is not None:
                params_list["applicationBoundaryScope"] = application_boundary_scope
        try:
            app_res = requests.get(application_list_url,
                                   headers=headers,
                                   params=params_list,
                                   timeout=60,
                                   verify=False)

            if _status_is_200(app_res.status_code):
                # extracting data in json format
                data = app_res.json()
                return data
            elif _status_is_429(app_res.status_code):
                self.exit_synctl(ERROR_CODE, TOO_MANY_REQUEST_ERROR)
            else:
                print('retrieve test summary list failed, status code:',
                      app_res.status_code)
                if app_res.text:
                    print(app_res.text)
                self.exit_synctl(ERROR_CODE)
        except requests.ConnectTimeout as timeout_error:
            self.exit_synctl(f"Connection to {host} timed out, error is {timeout_error}")
        except requests.ConnectionError as connect_error:
            self.exit_synctl(f"Connection to {host} failed, error is {connect_error}")

    def __get_all_application(self,
                              name_filter=None,
                              to=0,
                              page=1,
                              window_size=60*60*1000,
                              application_boundary_scope=None):
        """get all application list more than one pages"""
        total_hits = 0
        app_result = self.__get_application_list(to=to,
                                                 page=page,
                                                 window_size=window_size,
                                                 application_boundary_scope=application_boundary_scope)

        page = app_result["page"] if "page" in app_result else 1
        page_size = app_result["pageSize"] if "pageSize" in app_result else 200
        if "totalHits" in app_result:
            total_hits = app_result["totalHits"]

        if page_size >= total_hits:
            yield app_result
        else:
            total_pages = total_hits/page_size
            if (total_pages - round(total_pages)) > 0:
                total_pages += 1
            for page_x in range(0, round(total_pages)):
                if page_x == 0:  # first page
                    yield app_result
                else:
                    app_result = self.__get_application_list(page=page_x+1,
                                                             window_size=60*60*1000)
                    yield app_result

    def print_app_list(self, name_filter=None, to=0, window_size=60*60*1000):
        """show all applications, synctl get app"""
        id_length = 24
        label_length = 60
        app_count = 0  # count total application number
        print("id".upper().ljust(id_length),
              "label".upper().ljust(label_length),
              'Type'.upper())
        for app_res_gen in self.__get_all_application():
            if "items" in app_res_gen and len(app_res_gen["items"]) > 0:
                for i in app_res_gen["items"]:
                    print(i["id"].ljust(id_length),
                          i["label"].ljust(label_length),
                          i["entityType"], flush=True)
                    app_count += 1
        print(f"total app: {app_count}")


class Synctl:
    def __init__(self, args) -> None:
        self.args_list = args

        self.syn_instanace = None
        self.pop_instanace = None
        self.con_instanace = None
        self.syn_con_insta = None

    def get_all_args(self):
        return self.args_list

    def set_syn_instanace(self, ins):
        self.syn_instanace = ins

    def set_con_instanace(self, ins):
        self.syn_instanace = ins

    def set_pop_instanace(self, ins):
        self.pop_instanace = ins

    def set_syn_conf_instanace(self, ins):
        self.pop_instanace = ins

    def synctl_config(self):
        pass

    def synctl_create(self):
        pass

    def synctl_delete(self):
        pass

    def synctl_get(self):
        pass


class ParseParameter:

    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            prog='synctl', epilog='Use "synctl [command] --help" for more information about a command.')
        self.parser._positionals.title = 'commands'
        self.parser._optionals.title = 'options'

        sub_parsers = self.parser.add_subparsers(
            dest="sub_command",
            title="commands",
            help='[command] --help to show help')

        self.subparsers = sub_parsers

        self.parser_config = sub_parsers.add_parser(
            'config', help='Modify config file', usage=CONFIG_USAGE)
        self.parser_config._positionals.title = POSITION_PARAMS
        self.parser_config._optionals.title = OPTIONS_PARAMS

        self.parser_create = sub_parsers.add_parser(
            'create', help='create a Synthetic test, credential or alert', add_help=True, usage=CREATE_USAGE)
        self.parser_create._positionals.title = POSITION_PARAMS
        self.parser_create._optionals.title = OPTIONS_PARAMS

        self.parser_get = sub_parsers.add_parser(
            'get', help='get Synthetic test, location, credential, alert, pop-size or pop-cost', usage=GET_USAGE)
        self.parser_get._positionals.title = POSITION_PARAMS
        self.parser_get._optionals.title = OPTIONS_PARAMS

        self.parser_patch = sub_parsers.add_parser(
            'patch', help='patch a Synthetic test', usage=PATCH_USAGE)
        self.parser_patch._positionals.title = POSITION_PARAMS
        self.parser_patch._optionals.title = OPTIONS_PARAMS

        self.parser_update = sub_parsers.add_parser(
            'update', help='update a Synthetic test or alert', usage=UPDATE_USAGE)
        self.parser_update._positionals.title = POSITION_PARAMS
        self.parser_update._optionals.title = OPTIONS_PARAMS

        self.parser_delete = sub_parsers.add_parser(
            'delete', help='delete a Synthetic test, location, credential or alert', usage=DELETE_USAGE)
        self.parser_delete._positionals.title = POSITION_PARAMS
        self.parser_delete._optionals.title = OPTIONS_PARAMS

    def global_options(self):
        self.parser.add_argument(
            '--version', '-v', action="store_true", default=True, help="show version")

    def config_command_options(self):
        self.parser_config.add_argument(
            'config_type', choices=["set", "list", "use", "remove"], help='supported command')
        self.parser_config.add_argument(
            '--host', type=str, metavar="<host>", help='set hostname')
        self.parser_config.add_argument(
            '--token', '-t', type=str, metavar="<token>", help='set token')
        self.parser_config.add_argument(
            '--show-token', action='store_true', help='show token')
        self.parser_config.add_argument(
            '--env', '--name', type=str, metavar="<name>", help='specify which config to use')
        self.parser_config.add_argument(
            '--default', action="store_true", help='set as default')

    def create_command_options(self):
        self.parser_create.add_argument(
            "--verify-tls", action="store_true", default=False, help="verify tls certificate")
        self.parser_create.add_argument(
            'syn_type', type=str, choices=["test", "cred", "alert"], metavar="test/cred/alert", help="specify test/cred/alert")

        self.parser_create.add_argument(
            '-t', '--type', type=int, choices=[0, 1, 2, 3, 4, 5], required=False, metavar="<int>",
            help="Synthetic type: HTTPAction[0], HTTPScript[1], BrowserScript[2], WebpageScript[3], WebpageAction[4], SSLCertificate[5]")

        # support multiple locations
        # --location location_id_1 location_id_2 location_id_3
        # location cannot set required to True, due to --from-json can support location from json file
        self.parser_create.add_argument(
            '--location', type=str, nargs='+', required=False, metavar="id", help="location id, support multiple locations id")
        self.parser_create.add_argument(
            '--label', type=str, metavar="<string>", help="friendly name of the Synthetic test")
        self.parser_create.add_argument(
            '--description', '-d', type=str, metavar="<string>", help="the description of Synthetic test")
        self.parser_create.add_argument(
            '--frequency', type=int, metavar="<int>", help="the range is from 1 to 120 minute, default is 15. For SSLCertificate test, the default is 1440")
        self.parser_create.add_argument(
            '--apps', '--applications', '--app-id', '--application-id', type=str, nargs='+', metavar="<application-id>", help="application id, support multiple applications")
        self.parser_create.add_argument(
            '--websites', type=str, nargs='+', metavar="<website-id>", help="website id, support multiple websites")
        self.parser_create.add_argument(
            '--mobile-apps', '--mobile-applications' , type=str, nargs='+', metavar="<mobile-app-id>", help="mobile app id, support multiple mobile applications")
        # [0, 2]
        self.parser_create.add_argument(
            '--retries', type=int, choices=range(0, 3), metavar="<int>", help='retry times, value is [0, 2]')
        self.parser_create.add_argument(
            '--retry-interval', type=int, default=1, choices=range(1, 11), metavar="<int>", help="retry interval, range is [1, 10]")
        self.parser_create.add_argument(
            '--timeout', type=str, metavar="<num>ms|s|m", help='set timeout, accept <number>(ms|s|m)')
        self.parser_create.add_argument(
            '--custom-properties', type=str, metavar="<string>", help="An object with name/value pairs to provide additional information of the Synthetic test")

        # options for ping, url
        self.parser_create.add_argument(
            '--url', type=str, metavar="<url>", help='HTTP request URL')
        self.parser_create.add_argument(
            '--operation', type=str, metavar="<method>", help='HTTP request methods, GET, POST, HEAD, PUT, etc')
        self.parser_create.add_argument(
            '--follow-redirect', type=str, default="true", choices=["true", "false"], metavar="<boolean>", help='to allow redirect, true by default')

        self.parser_create.add_argument(
            '--headers', type=str, metavar="<json>", help="HTTP headers")

        self.parser_create.add_argument(
            '--body', type=str, metavar="<string>", help='HTTP body')

        # options for api script
        self.parser_create.add_argument(
            '-f', '--from-file', type=str, metavar="<file>", help='Synthetic payload from (.json) file')
        self.parser_create.add_argument(
            '--script', type=str, metavar="<file>", help='load script (.js/.side) from file')

        # options for bundle script
        self.parser_create.add_argument(
            '--bundle', type=str, metavar="<bundle>", help='Synthetic bundle test script, support zip file, zip file encoded with base64')
        self.parser_create.add_argument(
            '--bundle-entry-file', type=str, metavar="<filename>", help='Synthetic bundle test entry file, e.g, myscript.js')

        # expectStatus, expectJson, expectMatch, expectExists, expectNotEmpty
        self.parser_create.add_argument(
            '--expect-status', type=int, metavar="<int>", help='Synthetic test will fail if response status is not equal to expected status code, default 200')
        self.parser_create.add_argument(
            '--expect-json', type=str, metavar="<string>", help='An optional object to be used to check against the test response object')
        self.parser_create.add_argument(
            '--expect-match', type=str, metavar="<string>", help='An optional regular expression string to be used to check the test response')
        self.parser_create.add_argument(
            '--expect-exists', type=str, metavar="<string>", help='An optional list of property labels used to check if they are present in the test response object')
        self.parser_create.add_argument(
            '--expect-not-empty', type=str, metavar="<string>", help='An optional list of property labels used to check if they are present in the test response object with a non-empty value')
        self.parser_create.add_argument(
            '--allow-insecure', type=str, default='true', choices=['false', 'true'], metavar="<boolean>", help='if set to true then allow insecure certificates')
        self.parser_create.add_argument(
            '--validation-string', type=str, metavar="<string>", help='set validation-string')

        # browser type
        self.parser_create.add_argument(
            '--browser', type=str, choices=["chrome", "firefox"], metavar="<string>", default="chrome", help="browser type, support chrome and firefox")

        self.parser_create.add_argument(
            '--record-video', type=str, choices=['true', 'false'], metavar="<boolean>", help='set true to record video')

        # SSLCertificate
        self.parser_create.add_argument(
            '--hostname', type=str, metavar="<url>", help='set host name')
        self.parser_create.add_argument(
            '--port', type=int, help='set port')
        self.parser_create.add_argument(
            '--remaining-days-check', type=int, metavar="<int>", help='check remaining days for expiration of SSL certificate')

        self.parser_create.add_argument(
            '--key', type=str, metavar="<key>", help='set credential name')
        self.parser_create.add_argument(
            '--value', type=str, metavar="<value>", help='set credential value')

        # smart alerts
        self.parser_create.add_argument(
            '--name', type=str, metavar="<string>", help='friendly name for smart alert')

        self.parser_create.add_argument(
            '--test', type=str, nargs='+', metavar="<id>", help="test id, support multiple test id")

        self.parser_create.add_argument(
            '--window-size', type=str, default="1h", metavar="<window>", help="set Synthetic result window size, support [1,60]m, [1-24]h")

        self.parser_create.add_argument(
            '--alert-channel', type=str, nargs='+', metavar="<id>", help="alert channel id, support multiple alert channel id")

        self.parser_create.add_argument(
            '--severity', type=str, metavar="<string>", choices=["warning", "critical"], help="severity of alert")

        self.parser_create.add_argument(
            '--violation-count', type=int, metavar="<int>", help="the range is from 1 to 12 failures")

        self.parser_create.add_argument(
            '--tag-filter-expression', type=str, metavar="<json>", help="tag filter")

        # set auth
        self.parser_create.add_argument(
            '--use-env', '-e', type=str, default=None, metavar="<name>",help='use a specified configuration')
        self.parser_create.add_argument(
            '--host', type=str, metavar="<host>", help='set hostname')
        self.parser_create.add_argument(
            '--token', type=str, metavar="<token>", help='set token')


    def get_command_options(self):
        self.parser_get.add_argument(
            "--verify-tls", action="store_true", default=False, help="verify tls certificate")
        self.parser_get.add_argument(
            'op_type', choices=['location', 'lo', 'test', 'application', 'app', 'cred', 'alert', 'alert-channel', 'result', 'pop-size', 'size', 'pop-cost', 'cost'],
            help="command list")
        # parser_get.add_argument('type_id', type=str,
        #                         required=False, help='test id or location id')
        self.parser_get.add_argument(
            '--type', '-t', type=int, choices=[0, 1, 2, 3, 4, 5], metavar='<int>', help='Synthetic type, 0 HTTPAction, 1 HTTPScript, 2 BrowserScript, 3 WebpageScript, 4 WebpageAction, 5 SSLCertificate')
        self.parser_get.add_argument(
            'id', type=str, nargs="?", help='Synthetic test id')
        self.parser_get.add_argument(
            '--window-size', type=str, default="1h", metavar="<window>", help="set Synthetic result window size, support [1,60]m, [1-24]h"
        )

        self.parser_get.add_argument(
            '--save-script', action="store_true", help='save script to local disk, default file name is <label>.[js|json|side]')

        self.parser_get.add_argument(
            "--show-script", action='store_true', help="output test script to terminal")
        self.parser_get.add_argument(
            "--show-details", action='store_true', help="output test or location details to terminal")
        self.parser_get.add_argument(
            "--show-json", action='store_true', help="output test json to terminal")
        self.parser_get.add_argument(
            '--show-result', action='store_true', help="show latency and success rate")
        self.parser_get.add_argument(
            '--filter', nargs='?', default=None, help='filter by location')

        # result list
        self.parser_get.add_argument(
            '--test', type=str, nargs='?', metavar="id", help="test id")
        self.parser_get.add_argument(
            '--har', action="store_true", help="show har")

        # application
        application_group = self.parser_get.add_argument_group()
        application_group.add_argument(
            '--name-filter', type=str, metavar="<app>", help="filter application by name, only applicable for application name")
        # application_group

        host_token_group = self.parser_get.add_argument_group()
        # self.parser_get.add_argument(
        #     '--use-env', type=str, default=None, help='use a specified config')
        # self.parser_get.add_argument(
        #     '--host', type=str, help='set hostname')
        # self.parser_get.add_argument(
        #     '--token', type=str, help='set token')
        host_token_group.add_argument(
            '--use-env', '-e', type=str, default=None, metavar="<name>", help='use a specified config')
        host_token_group.add_argument(
            '--host', type=str,  metavar="<host>", help='set hostname')
        host_token_group.add_argument(
            '--token', type=str,  metavar="<token>", help='set token')

    def patch_command_options(self):
        self.parser_patch.add_argument(
            "--verify-tls", action="store_true", default=False, help="verify tls certificate")
        self.parser_patch.add_argument(
            'syn_type', type=str, choices=["test", "cred"], help="specify test/cred/")

        self.parser_patch.add_argument(
            'id', type=str, help="Synthetic test id")

        patch_exclusive_group = self.parser_patch.add_mutually_exclusive_group()
        # common options
        patch_exclusive_group.add_argument(
            '--active', type=str, choices=["false", "true"], metavar="<boolean>", help='set active')
        patch_exclusive_group.add_argument(
            '--frequency', type=int, metavar="<int>", help='set frequency')
        patch_exclusive_group.add_argument(
            '--location', nargs="+", metavar="<id>", help="set location")
        patch_exclusive_group.add_argument(
            '--description', type=str, metavar="<string>", help="set description")
        patch_exclusive_group.add_argument(
            '--label', type=str, metavar="<string>", help='set label')
        patch_exclusive_group.add_argument(
            '--retries', type=int, metavar="<int>", help="set retries, min is 0 and max is 2")
        patch_exclusive_group.add_argument(
            '--retry-interval', type=int, metavar="<int>", help="set retry-interval, min is 1, max is 10")
        # timeout Expected <number>(ms|s|m)
        patch_exclusive_group.add_argument(
            '--timeout', type=str, metavar="<num>ms|s|m", help='set timeout, accept <number>(ms|s|m)')
        patch_exclusive_group.add_argument(
            '--custom-properties', type=str, metavar="<string>", help="set custom property of a test")

        # API Simple
        patch_exclusive_group.add_argument(
            '--operation', type=str, metavar="<method>", help="HTTP request methods, GET, POST, HEAD, PUT, etc.")
        patch_exclusive_group.add_argument(
            '--mark-synthetic-call', type=str, metavar="<boolean>", help='set markSyntheticCall')
        patch_exclusive_group.add_argument(
            '--url', type=str, metavar="<url>", help="HTTP URL")
        patch_exclusive_group.add_argument(
            '--follow-redirect', type=str, metavar="<boolean>", help='set follow-redirect')
        patch_exclusive_group.add_argument(
            '--validation-string', type=str, metavar="<string>", help='set validation-string')
        patch_exclusive_group.add_argument(
            '--expect-status', type=int, metavar="<int>", help='set expected HTTP status code')
        patch_exclusive_group.add_argument(
            '--expect-json', type=str, metavar="<string>", help='An optional object to be used to check against the test response object')
        patch_exclusive_group.add_argument(
            '--expect-match', type=str, metavar="<string>", help='An optional regular expression string to be used to check the test response')
        patch_exclusive_group.add_argument(
            '--expect-exists', type=str, metavar="<string>", help='An optional list of property labels used to check if they are present in the test response object')
        patch_exclusive_group.add_argument(
            '--expect-not-empty', type=str, metavar="<string>", help='An optional list of property labels used to check if they are present in the test response object with a non-empty value')
        patch_exclusive_group.add_argument(
            '--allow-insecure', type=str, choices=['false', 'true'], metavar="<boolean>", help='if set to true then allow insecure certificates')

        # API Script / Browser test
        patch_exclusive_group.add_argument(
            '--record-video', type=str, choices=['true', 'false'], metavar="<boolean>", help='set true to record video')
        patch_exclusive_group.add_argument(
            '--browser', type=str, choices=["chrome", "firefox"], metavar="<string>", help="browser type, support chrome and firefox")
        patch_exclusive_group.add_argument(
            '--script', type=str, metavar="<filename>", help="specify a script file to update APIScript (.js), BrowserScript (.js) or WebpageScript (.side)")
        patch_exclusive_group.add_argument(
            '--bundle', type=str, metavar="<bundle>", help='set bundle')
        patch_exclusive_group.add_argument(
            '--bundle-entry-file', type=str, metavar="<string>", help="entry file of a bundle test")

        # SSL Certificate
        patch_exclusive_group.add_argument(
            '--hostname', type=str, metavar="<url>", help='set host name')
        patch_exclusive_group.add_argument(
            '--port', type=int, help='set port')
        patch_exclusive_group.add_argument(
            '--remaining-days-check', type=int, metavar="<int>", help='check remaining days for expiration of SSL certificate')

        # Patch cred
        patch_exclusive_group.add_argument(
            '--applications', '--apps', nargs="+", metavar="<id>", help="set applications")
        patch_exclusive_group.add_argument(
            '--websites', nargs="+", metavar="<id>", help="set websites")
        patch_exclusive_group.add_argument(
            '--mobile-apps', '--mobile-applications', nargs="+", metavar="<id>", help="set mobile applications")


        # parser_patch.add_mutually_exclusive_group
        self.parser_patch.add_argument(
            '--use-env', '-e', type=str, default=None, metavar="<name>", help='use a config hostname')
        self.parser_patch.add_argument(
            '--host', type=str, metavar="<host>", help='set hostname')
        self.parser_patch.add_argument(
            '--token', type=str, metavar="<token>", help='set token')

    def update_command_options(self):
        self.parser_update.add_argument(
            "--verify-tls", action="store_true", default=False, help="verify tls certificate")
        self.parser_update.add_argument(
            'syn_type', type=str, choices=["test", "alert", "cred"], help="Synthetic type/ smart alert/ credential")
        self.parser_update.add_argument(
            'id', type=str, help="Synthetic test id")

        update_exclusive_group = self.parser_update.add_mutually_exclusive_group()
        update_group = self.parser_update.add_argument_group()
        # common options
        update_group.add_argument(
            '--active', type=str, metavar="<boolean>", help='set active')
        update_group.add_argument(
            '--frequency', type=int, metavar="<int>", help='set frequency')
        update_group.add_argument(
            '--location', nargs="+", metavar="<id>", help="set location")
        update_group.add_argument(
            '--description', type=str, metavar="<string>", help="set description")
        update_group.add_argument(
            '--label', type=str, metavar="<string>", help='set label')
        update_group.add_argument(
            '--retries', type=int, metavar="<int>", help="set retries, min is 0 and max is 2")
        update_group.add_argument(
            '--retry-interval', type=int, metavar="<int>", help="set retry-interval, min is 1, max is 10")
        update_group.add_argument(
            '--timeout', type=str, metavar="<num>ms|s|m", help='set timeout, accept <number>(ms|s|m)')
        update_group.add_argument(
            '--custom-properties', type=str, metavar="<string>", help="set custom property of a test")
        update_group.add_argument(
            '--apps', '--applications', '--app-id', '--application-id', type=str, metavar="<application-id>", help="application id")
        update_group.add_argument(
            '--websites', type=str, nargs='+', metavar="<website-id>", help="website id, support multiple websites")
        update_group.add_argument(
            '--mobile-apps', '--mobile-applications', type=str, nargs='+', metavar="<mobile-app-id>", help="mobile app id, support multiple mobile applications")


        # API Simple
        update_group.add_argument(
            '--headers', type=str, metavar="<json>", help="HTTP headers")
        update_group.add_argument(
            '--body', type=str, metavar="<string>", help='HTTP body')
        update_group.add_argument(
            '--operation', type=str, metavar="<method>", help="HTTP request methods, GET, POST, HEAD, PUT, etc.")
        update_group.add_argument(
            '--mark-synthetic-call', type=str, metavar="<boolean>", help='set markSyntheticCall')
        update_group.add_argument(
            '--validation-string', type=str, metavar="<string>", help='set validation-string')
        update_group.add_argument(
            '--url', type=str, metavar="<url>", help="HTTP URL")
        update_group.add_argument(
            '--follow-redirect', type=str, metavar="<boolean>", help='set follow-redirect')
        update_group.add_argument(
            '--expect-status', type=int, metavar="<int>", help='set expected HTTP status code')
        update_group.add_argument(
            '--expect-json', type=str, metavar="<string>", help='An optional object to be used to check against the test response object')
        update_group.add_argument(
            '--expect-match', type=str, metavar="<string>", help='An optional regular expression string to be used to check the test response')
        update_group.add_argument(
            '--expect-exists', type=str, metavar="<string>", help='An optional list of property labels used to check if they are present in the test response object')
        update_group.add_argument(
            '--expect-not-empty', type=str, metavar="<string>", help='An optional list of property labels used to check if they are present in the test response object with a non-empty value')
        update_group.add_argument(
            '--allow-insecure', type=str, choices=['false', 'true'], metavar="<boolean>", help='if set to true then allow insecure certificates')

        # API Script / Browser test
        update_group.add_argument(
            '--record-video', type=str, choices=['true', 'false'], metavar="<boolean>", help='set true to record video')
        update_group.add_argument(
            '--browser', type=str, choices=["chrome", "firefox"], metavar="<string>", help="browser type, support chrome and firefox")
        update_group.add_argument(
            '-f', '--from-file', type=str, metavar="<filename>", help="Synthetic payload from (.json) file")
        update_group.add_argument(
            '--script', type=str, metavar="<filename>", help="specify a script file to update APIScript (.js), BrowserScript (.js) or WebpageScript (.side)")
        update_group.add_argument(
            '--bundle', type=str, metavar="<bundle>", help='set bundle')
        update_group.add_argument(
            '--bundle-entry-file', type=str, metavar="<string>", help="entry file of a bundle test")

        # SSL Certificate
        update_group.add_argument(
            '--hostname', type=str, metavar="<url>", help='set host name')
        update_group.add_argument(
            '--port', type=int, help='set port')
        update_group.add_argument(
            '--remaining-days-check', type=int, help='check remaining days for expiration of SSL certificate')

        # update alert
        update_group.add_argument(
            '--name', type=str, metavar="<string>", help='friendly name for smart alert')
        update_group.add_argument(
            '--test', type=str, nargs='+', metavar="id", help="test id, support multiple test id")
        update_group.add_argument(
            '--alert-channel', type=str, nargs='+', metavar="id", help="alert channel id, support multiple alert channel id")
        update_group.add_argument(
            '--severity', type=str, metavar="<string>", choices=["warning", "critical"], help="severity of alert")
        update_group.add_argument(
            '--violation-count', type=int, metavar="<int>", help="the range is from 1 to 12 failures")
        update_group.add_argument(
            '--tag-filter-expression', type=str, metavar="<json>", help="tag filter")
        # enable/disable smart alerts
        update_exclusive_group.add_argument(
            '--enable', action='store_true', help='enable smart alert')
        update_exclusive_group.add_argument(
            '--disable', action='store_true', help='disable smart alert')
        # update cred
        update_group.add_argument(
            '--value', type=str, metavar="<value>", help='set credential value')

        self.parser_update.add_argument(
            '--use-env', '-e', type=str, metavar="<name>", default=None, help='use a config hostname')
        self.parser_update.add_argument(
            '--host', type=str, metavar="<host>", help='set hostname')
        self.parser_update.add_argument(
            '--token', type=str, metavar="<token>", help='set token')

    def delete_command_options(self):
        self.parser_delete.add_argument(
            "--verify-tls", action="store_true", default=False, help="verify tls certificate")
        self.parser_delete.add_argument(
            'delete_type', choices=['location', 'lo', 'test', 'cred', 'alert'], help='specify Synthetic type: location/test/credential/smart alert')
        self.parser_delete.add_argument(
            'id', type=str, nargs="*", metavar="<id>", help='Synthetic test id, location id, credential name')

        # delete test in batch options
        delete_exclusive_group = self.parser_delete.add_mutually_exclusive_group()
        delete_exclusive_group.add_argument(
            '--match-regex', type=str, default=None, metavar="<regex>", help='use a regex to match Synthetic label')
        # only deletes tests full match location, if a test has two locations, include this, will
        # not be deleted
        delete_exclusive_group.add_argument(
            '--match-location', type=str, default=None, metavar="<id>", help='delete tests match this location id')
        delete_exclusive_group.add_argument(
            '--no-locations', action="store_true", help="delete tests with no locations")

        self.parser_delete.add_argument(
            '--use-env', '-e', type=str, default=None, metavar="<name>", help='specify a config name')
        self.parser_delete.add_argument(
            '--host', type=str, metavar="<host>", help='set hostname')
        self.parser_delete.add_argument(
            '--token', type=str, metavar="<token>", help='set token')

    def set_options(self):
        self.global_options()
        self.config_command_options()
        self.create_command_options()
        self.get_command_options()
        self.patch_command_options()
        self.update_command_options()
        self.delete_command_options()

    def get_parser(self):
        return self.parser


def ctrl_exit_handler(signal_received, frame):
    print("\nsynctl exited")
    sys.exit(0)

def main():
    """main function"""
    signal.signal(signal.SIGINT, ctrl_exit_handler)
    identify_hyphen()

    para_instanace = ParseParameter()
    para_instanace.set_options()
    get_args = para_instanace.get_parser().parse_args()
    update_args = get_args.__dict__.items()

    sys_args = sys.argv
    validate_args(sys_args)

    if len(sys_args) <= 1:
        general_helper()
        sys.exit(0)

    # show synctl version
    if '-v' in sys_args or '--version' in sys_args:
        show_version()
        sys.exit(NORMAL_CODE)

    pop_estimate = PopConfiguration()
    auth_instance = Authentication()

    syn_instance = SyntheticTest()
    alert_instance = SmartAlert()
    cred_instance = SyntheticCredential()
    patch_instance = PatchSyntheticTest()
    syn_update_instance = UpdateSyntheticTest()
    update_alert = UpdateSmartAlert()
    pop_instance = SyntheticLocation()

    summary_instance = SyntheticResult()
    app_instance = Application()


    # both host and token are required when using in command line
    if get_args.host is not None and get_args.token is not None:
        syn_instance.set_host_token(
            new_host=get_args.host, new_token=get_args.token)
        alert_instance.set_host_token(
            new_host=get_args.host, new_token=get_args.token)
        cred_instance.set_host_token(
            new_host=get_args.host, new_token=get_args.token)
        pop_instance.set_host_token(
            new_host=get_args.host, new_token=get_args.token)
        patch_instance.set_host_token(
            new_host=get_args.host, new_token=get_args.token)
        syn_update_instance.set_host_token(
            new_host=get_args.host, new_token=get_args.token)
        update_alert.set_host_token(
            new_host=get_args.host, new_token=get_args.token)
        summary_instance.set_host_token(
            new_host=get_args.host, new_token=get_args.token)
        app_instance.set_host_token(
            new_host=get_args.host, new_token=get_args.token)

    else:
        if COMMAND_CONFIG != get_args.sub_command:
            auth = auth_instance.get_auth(get_args.use_env)
            syn_instance.set_auth(auth)
            alert_instance.set_auth(auth)
            cred_instance.set_auth(auth)
            pop_instance.set_auth(auth)
            patch_instance.set_auth(auth)
            syn_update_instance.set_auth(auth)
            update_alert.set_auth(auth)
            summary_instance.set_auth(auth)
            app_instance.set_auth(auth)

            # set --verify-tls
            if get_args.verify_tls is not None :
                syn_instance.set_insecure(get_args.verify_tls)
                alert_instance.set_insecure(get_args.verify_tls)
                cred_instance.set_insecure(get_args.verify_tls)
                patch_instance.set_insecure(get_args.verify_tls)
                syn_update_instance.set_insecure(get_args.verify_tls)
                update_alert.set_insecure(get_args.verify_tls)
                pop_instance.set_insecure(get_args.verify_tls)
                app_instance.set_insecure(get_args.verify_tls)

    if COMMAND_CONFIG == get_args.sub_command:
        if get_args.config_type == "list":
            if get_args.show_token is True:
                if get_args.env is None:
                    auth_instance.print_config_file(show_token=True)
                else:
                    auth_instance.print_config_file(name=get_args.env, show_token=True)
            else:
                if get_args.env is None:
                    auth_instance.print_config_file()
                else:
                    auth_instance.print_config_file(name=get_args.env)
        elif get_args.config_type == "set":
            if get_args.host is None or get_args.env is None:
                print("--env and --host are required")
            else:
                if get_args.token is None:
                    get_args.token = getpass.getpass('Token:')
                set_as_default = False
                if get_args.default is True:
                    set_as_default = True
                auth_instance.add_an_item_to_config(
                    name=get_args.env,
                    host=get_args.host,
                    token=get_args.token,
                    set_default=set_as_default
                )
        elif get_args.config_type == "use":
            if get_args.env is None:
                print('--env is required when set it as default')
            else:
                auth_instance.set_env_to_default(get_args.env)
        elif get_args.config_type == "remove":
            if get_args.env is None:
                print('--env is required when remove a config')
            else:
                auth_instance.remove_an_item_from_config(get_args.env)

    elif COMMAND_GET == get_args.sub_command:
        if get_args.op_type == SYN_TEST:
            # synctl_instanace.synctl_get()
            # deal test
            syn_type_t = None
            syn_window_size = get_args.window_size
            if get_args.type is not None:
                try:
                    syn_type_t = synthetic_type[get_args.type]
                except IndexError:
                    print("Synthetic type only support 0 1 2 3 4 5", syn_type_t)

            if get_args.id is None:
                if get_args.filter is not None:
                    split_string = get_args.filter.split('=')
                    filtered_payload = syn_instance.retrieve_synthetic_test_by_filter(split_string)
                    syn_instance.print_synthetic_test(out_list=filtered_payload)
                    sys.exit(ERROR_CODE)

                out_list = syn_instance.retrieve_all_synthetic_tests(
                    syn_type_t)
                if get_args.show_result is True:
                    summary_result = summary_instance.get_summary_list(syn_window_size,
                                                                       test_id=get_args.id)
                    syn_instance.print_synthetic_test(out_list=out_list,
                                                      summary_list=summary_result)
                    sys.exit(NORMAL_CODE)
                syn_instance.print_synthetic_test(out_list=out_list)
            else:
                summary_result = summary_instance.get_summary_list(syn_window_size,
                                                                   test_id=get_args.id)
                # if get_args.id is not None:
                # a_single_payload type: list
                a_single_payload = syn_instance.retrieve_a_synthetic_test(
                    get_args.id)
                if get_args.show_script is True:
                    syn_instance.print_a_synthetic_details(
                        a_single_payload, show_script=True)
                elif get_args.show_json is True:
                    syn_instance.print_a_synthetic_details(
                        a_single_payload, show_json=True)
                elif get_args.save_script is True:
                    syn_instance.save_api_script_to_local(a_single_payload[0])
                elif get_args.show_details is True:
                    syn_instance.print_a_synthetic_details(
                        a_single_payload, show_details=True)
                else:
                    syn_instance.print_synthetic_test(out_list=a_single_payload,
                                                      test_type=syn_type_t,
                                                      summary_list=summary_result)
        elif get_args.op_type in (SYN_LOCATION, SYN_LO):
            # deal pop
            pop_locations_json = []
            if get_args.show_details is True:
                pop_location = pop_instance.retrieve_synthetic_locations(
                    get_args.id)
                pop_instance.print_a_location_details(
                    get_args.id, pop_location, show_details=True)
                syn_instance.exit_synctl(ERROR_CODE)
            if get_args.id is None:
                pop_locations_json = pop_instance.retrieve_synthetic_locations()
            else:
                pop_locations_json = pop_instance.retrieve_synthetic_locations(
                    location_id=get_args.id)
            pop_locations_summary_result = pop_instance.get_all_location_summary_list()
            pop_instance.print_synthetic_locations(
                pop_locations_json, pop_locations_summary_result)
        elif get_args.op_type in (SYN_APPLICATION, SYN_APP):
            if get_args.name_filter is not None:
                app_instance.set_name_filter(get_args.name_filter)
            app_instance.print_app_list()
        elif get_args.op_type == SYN_CRED:
            if get_args.id is None:
                if get_args.show_details is True:
                    cred_details = cred_instance.retrieve_credentials(get_args.show_details)
                    cred_instance.print_credentials(cred_details, get_args.show_details)
                else:
                    credentials = cred_instance.retrieve_credentials()
                    cred_instance.print_credentials(credentials)
            else:
                credential = cred_instance.retrieve_a_credential(get_args.id)
                cred_instance.print_a_credential(credential)
        elif get_args.op_type == SYN_ALERT:
            if get_args.id is None:
                alerts = alert_instance.retrieve_all_smart_alerts()
                alert_instance.print_synthetic_alerts(alerts)
            else:
                get_args.id = get_args.id.lstrip() if get_args.id.startswith(' ') else get_args.id
                single_alert = alert_instance.retrieve_a_smart_alert(get_args.id)
                if get_args.show_details is True:
                    alert_instance.print_a_alert_details(get_args.id, single_alert, show_details=True)
                elif get_args.show_json is True:
                    alert_instance.print_a_alert_details(get_args.id, single_alert, show_json=True)
                else:
                    alert_instance.print_synthetic_alerts(single_alert)
        elif get_args.op_type == "alert-channel":
            if get_args.id is None:
                alerting_channel = alert_instance.retrieve_all_alerting_channel()
                alert_instance.print_alerting_channels(alerting_channel)
            else:
                single_alert = alert_instance.retrieve_a_single_alerting_channel(get_args.id)
                alert_instance.print_alerting_channels([single_alert])
        # show test results
        elif get_args.op_type == SYN_RESULT:
            if get_args.test is not None:
                if get_args.window_size is None:
                    test_result = syn_instance.get_all_test_results(get_args.test)
                else:
                    test_result = syn_instance.get_all_test_results(get_args.test, get_args.window_size)
                if get_args.id is None:
                    syn_instance.print_result_list(test_result["items"])
                else:
                    if get_args.har is None:
                        a_result_details = syn_instance.retrieve_test_result_details(get_args.id, get_args.test)
                    else:
                        a_result_details = syn_instance.retrieve_test_result_details(get_args.id, get_args.test, get_args.har)
                    syn_instance.print_result_details(a_result_details, test_result["items"])
            else:
                print('testid is required')
        elif get_args.op_type == POP_SIZE or get_args.op_type == 'size':
            pop_estimate.print_estimated_pop_size()
        elif get_args.op_type == POP_COST or get_args.op_type == 'cost':
            pop_estimate.print_estimated_cost()
    elif COMMAND_CREATE == get_args.sub_command:

        if get_args.syn_type == SYN_CRED:
            cred_payload = CredentialConfiguration()
            if get_args.key is not None:
                cred_payload.set_credential_name(get_args.key)
            if get_args.value is not None:
                cred_payload.set_credential_value(get_args.value)
            if get_args.apps is not None:
                cred_payload.set_credential_applications(get_args.apps)
            if get_args.websites is not None:
                cred_payload.set_credential_websites(get_args.websites)
            if get_args.mobile_apps is not None:
                cred_payload.set_credential_mobile_apps(get_args.mobile_apps)

            cred_instance.set_cred_payload(payload=cred_payload.get_json())
            cred_instance.create_credential()
            return
        elif get_args.syn_type == SYN_ALERT:
            alert_payload = SmartAlertConfiguration()

            # --from-file, -f  options
            # create from a json file
            # if use a json file, all options should config in json
            if get_args.from_file is not None and get_args.from_file.endswith('.json') :
                json_file = get_args.from_file
                alert_payload.loads_from_json_file(json_file_name=json_file)
                syn_instance.set_synthetic_payload(
                    payload=alert_payload.get_json())
                alert_instance.set_alert_payload(alert_payload.get_json())
                alert_instance.create_synthetic_alert()
                return

            if get_args.name is not None:
                alert_payload.set_alert_name(get_args.name)
            if get_args.test is not None:
                alert_payload.set_synthetic_tests(get_args.test)
            if get_args.alert_channel is not None:
                alert_payload.set_alert_channel(get_args.alert_channel)
            if get_args.violation_count is not None:
                alert_payload.set_violations_count(get_args.violation_count)
            if get_args.severity is not None:
                alert_payload.set_severity(get_args.severity)
            if get_args.tag_filter_expression is not None:
                tag_filter_expression = get_args.tag_filter_expression
                tag_filter_expression_json = json.loads(tag_filter_expression)
                alert_payload.set_tag_filter_expression(tag_filter_expression_json)
            alert_instance.set_alert_payload(alert_payload.get_json())
            alert_instance.create_synthetic_alert()
        elif get_args.syn_type == SYN_TEST:
            if get_args.type is not None and get_args.type in [0, 1, 2, 3, 4, 5]:
                syn_type_t = synthetic_type[get_args.type]
                payload = SyntheticConfiguration(syn_type_t)

                # --from-file, -f  options
                # create from a json file
                # if use a json file, all options should config in json
                # not support provide other options from command-line
                if get_args.from_file is not None and get_args.from_file.endswith('.json') :
                    json_file = get_args.from_file
                    payload.loads_from_json_file(json_file_name=json_file)
                    syn_instance.set_synthetic_payload(
                        payload=payload.get_json())
                    syn_instance.create_a_synthetic_test()
                    return

                # create test and get option from command line
                # PING, create simple ping
                if get_args.type == 0 or get_args.type is None:
                    # request url is required
                    if get_args.url is not None:
                        payload.set_ping_url(get_args.url)
                    else:
                        payload.exit_synctl(ERROR_CODE, "URL is required")
                    if get_args.operation is not None:
                        payload.set_ping_operation(get_args.operation)
                    if get_args.headers is not None:
                        headers_str = get_args.headers
                        headers_json = json.loads(headers_str)
                        payload.set_ping_headers(headers_json)
                    if get_args.body is not None:
                        payload.set_ping_body(get_args.body)

                    # followRedirect
                    if get_args.follow_redirect is not None:
                        payload.set_follow_redirect(get_args.follow_redirect)
                    # expectStatus
                    if get_args.expect_status is not None:
                        payload.set_expect_status(get_args.expect_status)
                    # expectJson, str -> dict
                    # an example: --expect-json '{"name": "John","age": 30,"city": "New York"}'
                    if get_args.expect_json is not None:
                        expect_json_str = get_args.expect_json
                        expect_json_json = json.loads(expect_json_str)
                        payload.set_expect_json(expect_json=expect_json_json)
                    # expectMatch
                    # an example: --expect-match "ibm"
                    if get_args.expect_match is not None:
                        payload.set_expect_match(
                            expect_match=get_args.expect_match)
                    # expectExists
                    # an example: --expect-exists '["slideshow"]'
                    if get_args.expect_exists is not None:
                        expect_exists_str = get_args.expect_exists
                        expect_exists_list = json.loads(expect_exists_str)
                        payload.set_expect_exists(expect_exists_list)
                    # expectNotEmpty
                    # an example: --expect-not-empty '["slideshow"]'
                    if get_args.expect_not_empty is not None:
                        expect_not_empty_str = get_args.expect_not_empty
                        expect_not_empty_list = json.loads(
                            expect_not_empty_str)
                        payload.set_expect_not_empty(expect_not_empty_list)
                    if get_args.allow_insecure is not None:
                        payload.set_allow_insecure(get_args.allow_insecure)
                    if get_args.validation_string is not None:
                        payload.set_validation_string(get_args.validation_string)

                # basic type HTTPScript and WebpageScript
                elif get_args.type in (1, 2, 3) and get_args.bundle is None:
                    syn_type_t = synthetic_type[get_args.type]
                    payload = SyntheticConfiguration(syn_type=syn_type_t)
                    if get_args.script is not None:
                        script_content = payload.read_js_file(
                            get_args.script)
                        payload.set_api_script_script(
                            script_str=script_content)
                    if payload.get_api_script_script() == "":
                        syn_instance.exit_synctl(ERROR_CODE, "script should not be empty")

                # bundle script
                elif get_args.type in (1, 2) and get_args.bundle is not None:
                    syn_type_t = synthetic_type[get_args.type]
                    payload = SyntheticConfiguration(
                        syn_type_t, bundle_type=True)

                    if payload.is_zip_file(get_args.bundle):
                        bundle_base64_str = payload.read_zip_file_to_base64(
                            get_args.bundle)
                    else:
                        bundle_base64_str = get_args.bundle
                    # entry file
                    if get_args.bundle_entry_file is not None:
                        payload.set_api_bundle_script(
                            bundle_base64_str, script_file=get_args.bundle_entry_file)
                    else:
                        # script file use index.js
                        payload.set_api_bundle_script(bundle_base64_str)
                # BrowserScript 2, WebpageScript 3, WebpageAction 4
                if get_args.type in (2, 3, 4):
                    payload.set_browser_type(get_args.browser)

                    if get_args.record_video is not None:
                        payload.set_record_video(get_args.record_video)


                if get_args.type == 4:
                    if get_args.url is not None:
                        payload.set_ping_url(get_args.url)
                    else:
                        print("URL is required")

                if get_args.type == 5:
                    if get_args.hostname is not None:
                        payload.set_host(get_args.hostname)
                    if get_args.port is not None:
                        payload.set_port(get_args.port)
                    if get_args.remaining_days_check is not None:
                        payload.set_remaining_days(get_args.remaining_days_check)
                    payload.set_frequency(get_args.type, 1440)

                # global operation, add label, location, description, frequency, etc.
                if get_args.label is not None:
                    payload.set_label(get_args.label)
                if get_args.location is not None:
                    payload.set_locations(get_args.location)
                if get_args.description is not None:
                    payload.set_description(get_args.description)
                if get_args.frequency is not None:
                    payload.set_frequency(get_args.type, get_args.frequency)
                if get_args.apps is not None:
                    print("Warning: --app-id/--application-id will be deprecated soon. Use --apps/--applications")
                    payload.set_application_id(get_args.apps)
                if get_args.websites is not None:
                    payload.set_websites(get_args.websites)
                if get_args.mobile_apps is not None:
                    payload.set_mobile_apps(get_args.mobile_apps)
                if get_args.timeout is not None:
                    payload.set_timeout(get_args.timeout)

                if get_args.custom_properties is not None:
                    try:
                        payload.set_custom_properties(
                            json.loads(get_args.custom_properties))
                    except json.JSONDecodeError:
                        print(payload.exit_synctl("Ensure that the JSON string is properly formatted"))

                # configuration
                # retries [0, 2]
                if get_args.retries is not None:
                    payload.set_retries(get_args.retries)
                # retryInterval [0, 10]
                if get_args.retry_interval is not None:
                    payload.set_retry_interval(get_args.retry_interval)

                syn_payload = payload.get_json()
                syn_instance.set_synthetic_payload(payload=syn_payload)

                syn_instance.create_a_synthetic_test()

            else:
                syn_instance.exit_synctl(ERROR_CODE, '-t/--type is required to create synthetic test')
    elif COMMAND_PATCH == get_args.sub_command:
        if get_args.id is not None:
            patch_instance.set_test_id(get_args.id)
        if get_args.active is not None:
            patch_instance.patch_active(get_args.active)
        elif get_args.timeout is not None:
            # timeout Expected <number>(ms|s|m)
            patch_instance.patch_config_timeout(get_args.timeout)
        elif get_args.retries is not None:
            patch_instance.patch_retries(get_args.retries)
        elif get_args.frequency is not None:
            patch_instance.patch_frequency(get_args.frequency)
        elif get_args.retry_interval is not None:
            patch_instance.patch_retry_interval(get_args.retry_interval)
        elif get_args.operation is not None:
            patch_instance.patch_ping_operation(get_args.operation)
        elif get_args.script is not None:
            patch_instance.patch_script_from_file(get_args.script)
        elif get_args.description is not None:
            patch_instance.patch_description(get_args.description)
        elif get_args.record_video is not None:
            patch_instance.patch_record_video(get_args.record_video)
        elif get_args.browser is not None:
            patch_instance.patch_browser(get_args.browser)
        elif get_args.label is not None:
            patch_instance.patch_label(get_args.label)
        elif get_args.location is not None:
            patch_instance.patch_locations(get_args.location)
        elif get_args.mark_synthetic_call:
            patch_instance.patch_mark_synthetic_call(
                get_args.mark_synthetic_call)
        elif get_args.allow_insecure is not None:
            patch_instance.patch_allow_insecure(get_args.allow_insecure)
        elif get_args.expect_json is not None:
            patch_instance.patch_expect_json(get_args.expect_json)
        elif get_args.expect_not_empty is not None:
            patch_instance.patch_expect_not_empty(get_args.expect_not_empty)
        elif get_args.expect_exists is not None:
            patch_instance.patch_expect_exists(get_args.expect_exists)
        elif get_args.expect_match is not None:
            patch_instance.patch_expect_match(get_args.expect_match)
        elif get_args.expect_status is not None:
            patch_instance.patch_expect_status(get_args.expect_status)
        elif get_args.bundle is not None:
            patch_instance.patch_bundle(get_args.id, get_args.bundle)
        elif get_args.bundle_entry_file is not None:
            patch_instance.patch_bundle_entry_file(get_args.bundle_entry_file, get_args.id)
        elif get_args.url is not None:
            patch_instance.patch_url(get_args.url)
        elif get_args.follow_redirect is not None:
            patch_instance.patch_follow_redirect(get_args.follow_redirect)
        elif get_args.validation_string is not None:
            patch_instance.patch_validation_string(get_args.validation_string)
        elif get_args.custom_properties is not None:
            split_string = get_args.custom_properties.split(',')
            patch_instance.patch_custom_properties(get_args.id, split_string)
        elif get_args.hostname is not None:
            patch_instance.patch_host(get_args.id, get_args.hostname)
        elif get_args.port is not None:
            patch_instance.patch_port(get_args.id, get_args.port)
        elif get_args.remaining_days_check is not None:
            patch_instance.patch_remaining_days(get_args.id, get_args.remaining_days_check)
        if get_args.syn_type == SYN_CRED:
            if get_args.applications is not None:
                cred_instance.patch_applications(get_args.id, get_args.applications)
            if get_args.websites is not None:
                cred_instance.patch_websites(get_args.id, get_args.websites)
            if get_args.mobile_apps is not None:
                cred_instance.patch_mobile_apps(get_args.id, get_args.mobile_apps)
    elif COMMAND_UPDATE == get_args.sub_command:
        if get_args.syn_type == SYN_TEST:
            invalid_options = ["name", "severity", "alert_channel", "test", "violation_count"]
            syn_update_instance.invalid_update_options(invalid_options, update_args, syn_type=get_args.syn_type)
            if get_args.enable is True or get_args.disable is True:
                syn_update_instance.exit_synctl(ERROR_CODE, "option: --enable/--disable not supported by synthetic tests")
            payload = syn_instance.retrieve_a_synthetic_test(get_args.id)
            syn_update_instance.set_updated_payload(payload)
            # accept a full json payload
            if get_args.from_file is not None and get_args.from_file.endswith('.json'):
                new_payload = syn_update_instance.update_using_file(get_args.from_file)
                syn_update_instance.update_a_synthetic_test(get_args.id, new_payload)
            else:
                if get_args.label is not None:
                    syn_update_instance.update_label(get_args.label)
                if get_args.active is not None:
                    syn_update_instance.update_active(get_args.active)
                if get_args.timeout is not None:
                    syn_update_instance.update_config_timeout(get_args.timeout)
                if get_args.retries is not None:
                    syn_update_instance.update_retries(get_args.retries)
                if get_args.frequency is not None:
                    syn_update_instance.update_frequency(get_args.frequency)
                if get_args.retry_interval is not None:
                    syn_update_instance.update_retry_interval(get_args.retry_interval)
                if get_args.operation is not None:
                    syn_update_instance.update_ping_operation(get_args.operation)
                if get_args.script is not None:
                    syn_update_instance.update_config_script_file(get_args.script)
                if get_args.description is not None:
                    syn_update_instance.update_description(get_args.description)
                if get_args.record_video is not None:
                    syn_update_instance.update_record_video(get_args.record_video)
                if get_args.browser is not None:
                    syn_update_instance.update_browser(get_args.browser)
                if get_args.location is not None:
                    syn_update_instance.update_locations(get_args.location)
                if get_args.mark_synthetic_call:
                    syn_update_instance.update_mark_synthetic_call(get_args.mark_synthetic_call)
                if get_args.bundle is not None:
                    syn_update_instance.update_bundle(get_args.bundle)
                if get_args.bundle_entry_file is not None:
                    syn_update_instance.update_bundle_entry_file(get_args.bundle_entry_file)
                if get_args.url is not None:
                    syn_update_instance.update_url(get_args.url)
                if get_args.follow_redirect is not None:
                    syn_update_instance.update_follow_redirect(get_args.follow_redirect)
                if get_args.apps is not None:
                    print("Warning: --app-id/--application-id will be deprecated soon. Use --apps/--applications")
                    syn_update_instance.update_application_id(get_args.apps)
                if get_args.websites is not None:
                    syn_update_instance.update_websites(get_args.websites)
                if get_args.mobile_apps is not None:
                    syn_update_instance.update_mobile_app(get_args.mobile_apps)
                if get_args.expect_status is not None:
                    syn_update_instance.update_expect_status(get_args.expect_status)
                if get_args.allow_insecure is not None:
                    syn_update_instance.update_allow_insecure(get_args.allow_insecure)
                if get_args.expect_json is not None:
                    syn_update_instance.update_expect_json(get_args.expect_json)
                if get_args.expect_not_empty is not None:
                    syn_update_instance.update_expect_not_empty(get_args.expect_not_empty)
                if get_args.expect_exists is not None:
                    syn_update_instance.update_expect_exists(get_args.expect_exists)
                if get_args.expect_match is not None:
                    syn_update_instance.update_expect_match(get_args.expect_match)
                if get_args.validation_string is not None:
                    syn_update_instance.update_validation_string(get_args.validation_string)
                if get_args.custom_properties is not None:
                    split_string = get_args.custom_properties.split(',')
                    syn_update_instance.update_custom_properties(split_string)
                if get_args.body is not None:
                    syn_update_instance.update_body(get_args.body)
                if get_args.headers is not None:
                    split_string = get_args.headers.split(',')
                    syn_update_instance.update_headers(split_string)
                if get_args.hostname is not None:
                    syn_update_instance.update_host(get_args.hostname)
                if get_args.port is not None:
                    syn_update_instance.update_port(get_args.port)
                if get_args.remaining_days_check is not None:
                    syn_update_instance.update_remaining_days(get_args.remaining_days_check)
                updated_payload = syn_update_instance.get_updated_test_config()
                syn_update_instance.update_a_synthetic_test(get_args.id, updated_payload)
        if get_args.syn_type == SYN_ALERT:
            get_args.id = get_args.id.lstrip() if get_args.id.startswith(' ') else get_args.id
            invalid_options = ["label", "active", "frequency", "timeout", "retry_interval", "retries", "operation", "script_file",
                               "location", "record_video", "mark_synthetic_call", "entry_file", "url", "follow_redirect",
                               "expect_status", "validation_string", "bundle", "custom_properties"]
            syn_update_instance.invalid_update_options(invalid_options, update_args, syn_type=get_args.syn_type)
            payload = alert_instance.retrieve_a_smart_alert(get_args.id)
            update_alert.set_updated_payload(payload)
            if get_args.from_file is not None and get_args.from_file.endswith('.json'):
                new_payload = update_alert.update_using_file(get_args.from_file)
                update_alert.update_a_smart_alert(get_args.id, new_payload)
            elif get_args.enable is True or get_args.disable is True:
                operation = "enable" if get_args.enable else "disable"
                invalid_options = ["name", "severity", "alert_channel", "test", "violation_count"]
                syn_update_instance.invalid_update_options(invalid_options, update_args, toggle=operation)
                update_alert.toggle_smart_alert(get_args.id, operation)
            else:
                if get_args.name is not None:
                    update_alert.update_alert_name(get_args.name)
                if get_args.description is not None:
                    update_alert.update_description(get_args.description)
                if get_args.severity is not None:
                    update_alert.update_alert_severity(get_args.severity)
                if get_args.alert_channel is not None:
                    update_alert.update_alert_channel(get_args.alert_channel)
                if get_args.test is not None:
                    update_alert.update_tests(get_args.test)
                if get_args.violation_count is not None:
                    update_alert.update_violation_count(get_args.violation_count)
                if get_args.tag_filter_expression is not None:
                    tag_filter_expression = json.loads(get_args.tag_filter_expression)
                    update_alert.update_tag_filter_expression(tag_filter_expression)
                updated_alert_config = update_alert.get_updated_alert_config()
                update_alert.update_a_smart_alert(get_args.id, updated_alert_config)
        if get_args.syn_type == SYN_CRED:
            cred_payload = CredentialConfiguration()
            if get_args.value is not None:
                cred_payload.set_credential_name(get_args.id)
                cred_payload.set_credential_value(get_args.value)

            cred_instance.set_cred_payload(payload=cred_payload.get_json())
            cred_instance.update_a_credential(get_args.id)
    elif COMMAND_DELETE == get_args.sub_command:
        if get_args.delete_type == SYN_TEST:
            if get_args.id is not None and len(get_args.id) > 0:
                syn_instance.delete_multiple_synthetic_tests(
                    get_args.id)
            elif get_args.match_regex is not None:
                syn_instance.delete_tests_label_match_regex(
                    label_regex=get_args.match_regex)
            elif get_args.match_location is not None:
                syn_instance.delete_tests_match_location(
                    match_location=get_args.match_location)
            elif get_args.no_locations is True:
                syn_instance.delete_tests_without_location()
            else:
                print('no synthetic test to delete')

        if get_args.delete_type in (SYN_LOCATION, SYN_LO):
            if get_args.id is not None:
                pop_instance.delete_synthetic_locations(get_args.id)
        if get_args.delete_type == SYN_CRED:
            if get_args.id is not None:
                cred_instance.delete_credentials(get_args.id)
        if get_args.delete_type == SYN_ALERT:
            if get_args.id is not None and len(get_args.id) > 0:
                get_args.id = [a.lstrip() if a.startswith(' ') else a for a in get_args.id]
                alert_instance.delete_multiple_smart_alerts(get_args.id)
            else:
                print('no smart alert to delete')

    else:
        print('unknown command:', get_args.sub_command)

if __name__ == "__main__":
    main()
