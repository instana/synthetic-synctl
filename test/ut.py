#!/usr/bin/env python3
from synctl import ParseParameter, SyntheticConfiguration, SyntheticTest
from synctl import synthetic_type

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
            '--label', 'ibm-simple-ping'])
        self.assertEqual(get_args.sub_command, 'create')

        syn_type_t = synthetic_type[get_args.type]
        payload = SyntheticConfiguration(syn_type_t)
        payload.set_label(get_args.label)
        payload.set_ping_url(get_args.url)
        payload.set_locations(get_args.location)
        payload.set_frequency(get_args.frequency)

        syn_payload= json.loads(payload.get_json())
        self.assertEqual(syn_payload['label'], 'ibm-simple-ping')

        self.assertEqual(syn_payload['locations'][0], 'N2I5Uc12K8W6qh2dklkh')
        self.assertEqual(syn_payload['configuration']['url'], 'https://www.ibm.com')
        self.assertEqual(syn_payload['configuration']['syntheticType'], synthetic_type[0])
        self.assertEqual(syn_payload['testFrequency'], 5)
        syn_instance = SyntheticTest()
        syn_instance.set_synthetic_payload(payload=syn_payload)


if __name__ == '__main__':
    unittest.main()
