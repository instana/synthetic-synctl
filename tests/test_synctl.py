#!/usr/bin/env python3
from synctl import ParseParameter, SyntheticConfiguration, SyntheticTest
from synctl import synthetic_type
from pathlib import Path

import unittest
import json

class TestStringMethods(unittest.TestCase):

    def test_type(self):
        self.assertEqual(synthetic_type[0], 'HTTPAction')
        self.assertEqual(synthetic_type[1], 'HTTPScript')
        self.assertEqual(synthetic_type[2], 'BrowserScript')
        self.assertEqual(synthetic_type[3], 'WebpageScript')
        self.assertEqual(synthetic_type[4], 'WebpageAction')

    def test_create_simple_ping_01(self):
        para_instanace = ParseParameter()
        para_instanace.set_options()
        get_args = para_instanace.get_parser().parse_args([
            'create', 'test',
            '-t', 0,'--frequency', '5',
            '--url', 'https://www.ibm.com',
            '--lo', 'N2I5Uc12K8W6qh2dklkh',
            '--label', 'ibm-simple-ping',
            '--retries', '1',
            '--retry-interval', '5',
            '--timeout', '10m',
            '--follow-redirect', 'true'
            ])

        self.assertEqual(get_args.sub_command, 'create')

        syn_type_t = synthetic_type[get_args.type]
        payload = SyntheticConfiguration(syn_type_t)
        payload.set_label(get_args.label)
        payload.set_ping_url(get_args.url)
        payload.set_locations(get_args.location)
        payload.set_frequency(get_args.frequency)
        payload.set_retries(get_args.retries)
        payload.set_retry_interval(get_args.retry_interval)
        payload.set_timeout(get_args.timeout)
        payload.set_follow_redirect(get_args.follow_redirect)

        syn_payload = json.loads(payload.get_json())
        self.assertEqual(syn_payload['label'], 'ibm-simple-ping')

        self.assertEqual(syn_payload['locations'][0], 'N2I5Uc12K8W6qh2dklkh')
        self.assertEqual(syn_payload['configuration']['url'], 'https://www.ibm.com')
        self.assertEqual(syn_payload['configuration']['syntheticType'], synthetic_type[0])
        self.assertEqual(syn_payload['testFrequency'], 5)
        self.assertEqual(syn_payload['configuration']['retries'], 1)
        self.assertEqual(syn_payload['configuration']['retryInterval'], 5)
        self.assertEqual(syn_payload['configuration']['timeout'], '10m')
        self.assertEqual(syn_payload['configuration']['followRedirect'], True)
        syn_instance = SyntheticTest()
        syn_instance.set_synthetic_payload(payload=syn_payload)

    def test_create_api_script(self):
        para_instanace = ParseParameter()
        para_instanace.set_options()
        get_args = para_instanace.get_parser().parse_args([
            'create', 'test',
            '-t', '1',
            '--frequency', '5',
            '--lo', 'N2I5Uc12K8W6qh2dklkh',
            '--label', 'synthetic-api-script-test',
            '-f', '../examples/http-scripts/http-get.js'
            ])
        self.assertEqual(get_args.sub_command, 'create')

        syn_type_t = synthetic_type[get_args.type]
        payload = SyntheticConfiguration(syn_type_t, bundle_type=False)
        payload.set_label(get_args.label)
        payload.set_locations(get_args.location)
        payload.set_frequency(get_args.frequency)

        with open(Path(get_args.from_file).resolve(), "r", encoding="utf-8") as file1:
            script_str = file1.read()
            payload.set_api_script_script(script_str)

        syn_payload = json.loads(payload.get_json())

        self.assertEqual(syn_payload['label'], 'synthetic-api-script-test')
        self.assertEqual(syn_payload['locations'][0], 'N2I5Uc12K8W6qh2dklkh')
        self.assertEqual(syn_payload['configuration']['syntheticType'], synthetic_type[1])
        self.assertEqual(syn_payload['testFrequency'], 5)

        syn_instance = SyntheticTest()
        syn_instance.set_synthetic_payload(payload=syn_payload)

    def test_create_bundle_test(self):
        para_instanace = ParseParameter()
        para_instanace.set_options()
        get_args = para_instanace.get_parser().parse_args([
            'create', 'test',
            '-t', '1','--frequency', '5',
            '--lo', 'N2I5Uc12K8W6qh2dklkh',
            '--label', 'synthetic-bundle-test',
            '--bundle', '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',
            '--bundle-entry-file', 'index.js',
            '--expect-status', '501',
            '--expect-json', '{"slideshow": {"date": "date of publication", "title": "Sample Slide Show", "author": "Yours Truly", "slides": [{"type": "all", "title": "Wake up to WonderWidgets!"}, {"type": "all", "items": ["Why <em>WonderWidgets</em> are great", "Who <em>buys</em> WonderWidgets"], "title": "Overview"}]}}',
            '--expect-match', 'Coding in Javascript',
            '--allow-insecure', 'true'
            ])
        self.assertEqual(get_args.sub_command, 'create')

        syn_type_t = synthetic_type[get_args.type]
        payload = SyntheticConfiguration(syn_type_t, bundle_type=True)
        payload.set_label(get_args.label)
        payload.set_locations(get_args.location)
        payload.set_frequency(get_args.frequency)
        payload.set_api_bundle_script(get_args.bundle, get_args.script_file)
        payload.set_expect_status(get_args.expect_status)
        payload.set_expect_json(get_args.expect_json)
        payload.set_expect_match(get_args.expect_match)
        payload.set_allow_insecure(get_args.allow_insecure)

        syn_payload = json.loads(payload.get_json())

        self.assertEqual(syn_payload['label'], 'synthetic-bundle-test')
        self.assertEqual(syn_payload['locations'][0], 'N2I5Uc12K8W6qh2dklkh')
        self.assertEqual(syn_payload['configuration']['syntheticType'], synthetic_type[1])
        self.assertEqual(syn_payload['testFrequency'], 5)
        self.assertEqual(syn_payload['configuration']['scripts']['bundle'], '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')
        self.assertEqual(syn_payload['configuration']['scripts']['scriptFile'], 'index.js')
        self.assertEqual(syn_payload['configuration']['expectStatus'], 501)
        self.assertEqual(syn_payload['configuration']['expectJson'], '{"slideshow": {"date": "date of publication", "title": "Sample Slide Show", "author": "Yours Truly", "slides": [{"type": "all", "title": "Wake up to WonderWidgets!"}, {"type": "all", "items": ["Why <em>WonderWidgets</em> are great", "Who <em>buys</em> WonderWidgets"], "title": "Overview"}]}}')
        self.assertEqual(syn_payload['configuration']['expectMatch'], 'Coding in Javascript')
        self.assertEqual(syn_payload['configuration']['allowInsecure'], True)
        syn_instance = SyntheticTest()
        syn_instance.set_synthetic_payload(payload=syn_payload)

    def test_create_browser_bundle(self):
        para_instanace = ParseParameter()
        para_instanace.set_options()
        get_args = para_instanace.get_parser().parse_args([
            'create', 'test', '-t', '2',
            '--label', 'browser-script-test-bundle',
            '--location', 'N2I5Uc12K8W6qh2dklkh',
            '--frequency', '5',
            '--browser', 'firefox',
            '--bundle', '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',
            '--bundle-entry-file', 'mytest.js'
    ])
        self.assertEqual(get_args.sub_command, 'create')

        syn_type_t = synthetic_type[get_args.type]
        payload = SyntheticConfiguration(syn_type_t, bundle_type=True)
        payload.set_label(get_args.label)
        payload.set_locations(get_args.location)
        payload.set_browser_type(get_args.browser)
        payload.set_frequency(get_args.frequency)
        payload.set_api_bundle_script(get_args.bundle, get_args.script_file)

        syn_payload = json.loads(payload.get_json())

        self.assertEqual(syn_payload['label'], 'browser-script-test-bundle')
        self.assertEqual(syn_payload['locations'][0], 'N2I5Uc12K8W6qh2dklkh')
        self.assertEqual(syn_payload['configuration']['syntheticType'], synthetic_type[2])
        self.assertEqual(syn_payload['testFrequency'], 5)
        self.assertEqual(syn_payload['configuration']['browser'], 'firefox')
        self.assertEqual(syn_payload['configuration']['scripts']['bundle'], 'UEsDBAoAAAAAAOiGTFUAAAAAAAAAAAAAAAAOABwAYnVuZGxlLXRlc3QwMS9VVAkAA/SARmP1gEZjdXgLAAEE9QEAAAQUAAAAUEsDBBQAAAAIAOCmTFVLcg0lsQAAAGoBAAAWABwAYnVuZGxlLXRlc3QwMS9pbmRleC5qc1VUCQADJLlGYyS5RmN1eAsAAQT1AQAABBQAAAB9zs0KwjAMB/D7nqKHQStIh/OmyBBPgriLL7DO6Apdq23mx9u7FEF0slPT9PdPWjsbkJ0dztiKebh22oPgMjNaZdTlk2VSR9MgXvIhoisEzD9Qq3Y+dNQlk9BU0RdxHhX0QmeSVoheqw4hyAAoeAPGOD5l/O68OcY0rXAGpLYnJ7ipFJgepOFpsQHU9fsXY6SQsVdIW7Xw3zPrkMFDB1yMRn+yYG/fXu7KzfqwLfe9fQFQSwMECgAAAAAA1aZMVQAAAAAAAAAAAAAAABIAHABidW5kbGUtdGVzdDAxL2xpYi9VVAkAAxG5RmMSuUZjdXgLAAEE9QEAAAQUAAAAUEsDBBQAAAAIAMumTFX5mkDz8QAAAKcBAAAZABwAYnVuZGxlLXRlc3QwMS9saWIvaWJtMy5qc1VUCQAD/bhGYxO5RmN1eAsAAQT1AQAABBQAAABVUEFuwyAQvPOKPVQCSxaO2lutntKeesgbCKxbSzbrwiInqvL3gh27CqdlZnY0O5Z8ZDAxYmB4g4A/qQ+o5IrIqhVNA3YRFQ7jg+oOyUoU2YAMT9/M012SmVZ0yVvuyUMhXlQFvwJWlf5CVrJM8bVp5nnW/XnUlkZZZwnAtqkwhDobxinHwBrO5K6rTXl9B0XwD8ASlwbUGaawkO3OBeQU/Pa/iceN3nekPM7wbhhVVYOM6N1+uSOPcjdbK9KZM4Pa4unIhlM8kstJnw+HbPFxmdAyOjAFgNPnfsvmVWLk8SbESC6V5JeJAsfc49JaK/4AUEsDBBQAAAAIAMamTFUlcJfDtAAAAAQBAAAZABwAYnVuZGxlLXRlc3QwMS9saWIvZ290MS5qc1VUCQAD87hGY/S4RmN1eAsAAQT1AQAABBQAAAAtjkEOgyAQRfecYuIGTBqJW0x7F6pUaShjYYw1hrsXaDcMkP/fvBF9JJiR4ArBvDcbjOD5yduBMR0PP8Jj8yNZ9CXVixZOBjDW2jlp0ik39a5tpXQrRhJ8IVqjkrLMu/Udhllqf9Bi/cwvlQDwjOjV/w6wGOdQAd8xuInXz5TP1HYlJ4rOby060zmcq2WfnePmKDOLSg4BSHm9wdlUXqOgqcAmscTYC6ctt81nxUAxexfEwL5QSwMEFAAAAAgABKZMVfkY0sj6AAAAuwEAAB0AHABidW5kbGUtdGVzdDAxL2xpYi9yZXF1ZXN0Mi5qc1VUCQADiLdGYwm5RmN1eAsAAQT1AQAABBQAAABVUM1OxCAQvvMUczCBJg3d7NHGk+vJg89AYapNWqbCkK4x++5Cu63Kafj+8s1Y8pHBxIiB4QkCfqYhoJIbIqtWiKaBngKMZM0IjJELYldfkWfgr/EOyaqoRmR4+GCe74pM5MA+ecsDeSjMWVXwLWCT6XdkJcsUH5tmWRbdmcElbWmSdRYB7F6FIdQ5M865CNbQkfvagsobeiiCXwDWwjSizjCFlWwPLiCn4Pf/Tfx3DL4n5XGBi2FUVQ1y6KZjdUce5ZG1nU1nzoxqb6cjG07xmVwuej6dcsLLdUbL6MAUAN5ej1X2rNIijzchJnKpFL/OFDjmS65na8UPUEsBAh4DCgAAAAAA6IZMVQAAAAAAAAAAAAAAAA4AGAAAAAAAAAAQAO1BAAAAAGJ1bmRsZS10ZXN0MDEvVVQFAAP0gEZjdXgLAAEE9QEAAAQUAAAAUEsBAh4DFAAAAAgA4KZMVUtyDSWxAAAAagEAABYAGAAAAAAAAQAAAKSBSAAAAGJ1bmRsZS10ZXN0MDEvaW5kZXguanNVVAUAAyS5RmN1eAsAAQT1AQAABBQAAABQSwECHgMKAAAAAADVpkxVAAAAAAAAAAAAAAAAEgAYAAAAAAAAABAA7UFJAQAAYnVuZGxlLXRlc3QwMS9saWIvVVQFAAMRuUZjdXgLAAEE9QEAAAQUAAAAUEsBAh4DFAAAAAgAy6ZMVfmaQPPxAAAApwEAABkAGAAAAAAAAQAAAKSBlQEAAGJ1bmRsZS10ZXN0MDEvbGliL2libTMuanNVVAUAA/24RmN1eAsAAQT1AQAABBQAAABQSwECHgMUAAAACADGpkxVJXCXw7QAAAAEAQAAGQAYAAAAAAABAAAApIHZAgAAYnVuZGxlLXRlc3QwMS9saWIvZ290MS5qc1VUBQAD87hGY3V4CwABBPUBAAAEFAAAAFBLAQIeAxQAAAAIAASmTFX5GNLI+gAAALsBAAAdABgAAAAAAAEAAACkgeADAABidW5kbGUtdGVzdDAxL2xpYi9yZXF1ZXN0Mi5qc1VUBQADiLdGY3V4CwABBPUBAAAEFAAAAFBLBQYAAAAABgAGACkCAAAxBQAAAAA=')
        self.assertEqual(syn_payload['configuration']['scripts']['scriptFile'], 'mytest.js')

        syn_instance = SyntheticTest()
        syn_instance.set_synthetic_payload(payload=syn_payload)


    def test_create_browser_script(self):
        para_instanace = ParseParameter()
        para_instanace.set_options()
        get_args = para_instanace.get_parser().parse_args([
            'create', 'test',
            '-t', '2',
            '--label', 'browser-script-test',
            '--location', 'N2I5Uc12K8W6qh2dklkh',
            '--frequency', '10',
            '--browser', 'firefox',
            '--from-file', '../examples/browserscripts/api-sample.js'
        ])
        self.assertEqual(get_args.sub_command, 'create')

        syn_type_t = synthetic_type[get_args.type]
        payload = SyntheticConfiguration(syn_type_t, bundle_type=False)
        payload.set_label(get_args.label)
        payload.set_locations(get_args.location)
        payload.set_browser_type(get_args.browser)
        payload.set_frequency(get_args.frequency)

        # read script
        with open(Path(get_args.from_file).resolve(), "r", encoding="utf-8") as file1:
            script_str = file1.read()
            payload.set_api_script_script(script_str)

        syn_payload = json.loads(payload.get_json())

        self.assertEqual(syn_payload['label'], 'browser-script-test')
        self.assertEqual(syn_payload['locations'][0], 'N2I5Uc12K8W6qh2dklkh')
        self.assertEqual(syn_payload['configuration']['syntheticType'], synthetic_type[2])
        self.assertEqual(syn_payload['testFrequency'], 10)
        self.assertEqual(syn_payload['configuration']['browser'], 'firefox')

        syn_instance = SyntheticTest()
        syn_instance.set_synthetic_payload(payload=syn_payload)

    def test_create_webpage_action(self):
        """webpage action test"""
        para_instanace = ParseParameter()
        para_instanace.set_options()
        get_args = para_instanace.get_parser().parse_args([
            'create', 'test',
            '-t', '4',
            '--label', 'webpage-simple-test',
            '--location', 'N2I5Uc12K8W6qh2dklkh',
            '--frequency', '10',
            '--browser', 'firefox',
            '--url', 'https://www.ibm.com'
        ])
        self.assertEqual(get_args.sub_command, 'create')

        syn_type_t = synthetic_type[get_args.type]
        payload = SyntheticConfiguration(syn_type_t, bundle_type=False)
        payload.set_label(get_args.label)
        payload.set_locations(get_args.location)
        payload.set_browser_type(get_args.browser)
        payload.set_frequency(get_args.frequency)

        payload.set_ping_url(get_args.url)


        syn_payload = json.loads(payload.get_json())

        self.assertEqual(syn_payload['label'], 'webpage-simple-test')
        self.assertEqual(syn_payload['locations'][0], 'N2I5Uc12K8W6qh2dklkh')
        self.assertEqual(syn_payload['configuration']['syntheticType'], synthetic_type[4])
        self.assertEqual(syn_payload['testFrequency'], 10)
        self.assertEqual(syn_payload['configuration']['browser'], 'firefox')
        self.assertEqual(syn_payload['configuration']['url'], 'https://www.ibm.com')

        syn_instance = SyntheticTest()
        syn_instance.set_synthetic_payload(payload=syn_payload)

if __name__ == '__main__':
    unittest.main()
