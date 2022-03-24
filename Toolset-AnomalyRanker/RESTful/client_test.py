# -*- coding: utf-8 -*-
"""The module that runs the RESTful API tests from the client side.

Example:
    $ python3 client_test.py
"""
import os
import sys
import json
import configparser
from urllib.parse import urljoin
import requests


config = configparser.RawConfigParser()
if os.path.isfile('config'):
    config.read('config')
else:
    print("Config file not exist! Abort.")
    sys.exit(-1)

if config.has_option('restful', 'test_url'):
    test_url = config.get('restful', 'test_url')
else:
    print("Option [restful]/test_url not exist! Abort.")
    sys.exit(-1)


def single_test(api, scenario):
    """Send a given json to the target url and get the response.

    Args:
        api(str): the API that will be used for the RESTful test, e.g. reset,
            predict.
        scenario(str): the json file that will be used, which is placed under
            RESTful/scenario

    Returns:
        The response object of the request.
    """
    global test_url
    json_path = os.path.join('RESTful/scenarios',
                             api,
                             scenario + '.json')
    if not os.path.isfile(json_path):
        print("Test json {f} not exist! Abort.".format(f=json_path))
        sys.exit(-1)
    with open(json_path) as json_file:
        json_data = json.load(json_file)

    api_url = urljoin(test_url, api)
    try:
        r = requests.post(api_url, json=json_data)
    except (requests.exceptions.InvalidSchema,
            requests.exceptions.ConnectionError) as e:
        print("Connection fails! Abort. Error Msg:")
        print(str(e))
        sys.exit(-1)

    return r


def test(test_json_name):
    """Test a set of scenarios which are defined in a json file.

    Args:
        test_json_name(str): The name of the json file to be tested, placed
        under RESTful/tests/

    Returns:
        True if all tested scenarios are successful, otherwise False.
    """
    print(('======{test_name}======'.format(test_name=test_json_name.upper())))
    test_json_path = os.path.join('RESTful/tests', test_json_name + '.json')
    if not os.path.isfile(test_json_path):
        print("Test json {f} not exist! Abort.".format(f=test_json_path))
        sys.exit(-1)

    with open(test_json_path) as json_file:
        json_data = json.load(json_file)

    if not isinstance(json_data, list):
        print("Test json should be a list! Abort.")
        sys.exit(-1)

    if not all(map(lambda x: isinstance(x, dict) and
                   'api' in x and
                   'scenario' in x and
                   'expected_code' in x,
                   json_data)):
        print(("Every element in the test json should be a dictionary "
               "that contains keys 'api', 'scenario' and 'expected_code'! "
               "Abort."))
        sys.exit(-1)

    overall_succeed = True
    for i, test_item in enumerate(json_data):
        r = single_test(test_item['api'], test_item['scenario'])

        response_code = r.status_code
        try:
            response_json = r.json()
        except ValueError:
            response_json = None

        if isinstance(test_item['expected_code'], list):
            succeed = response_code in test_item['expected_code']
        else:
            succeed = response_code == test_item['expected_code']

        overall_succeed = overall_succeed and succeed

        print("Scenario {test_num}: {api}/{scenario}"
              .format(test_num=str(i+1),
                      api=test_item['api'],
                      scenario=test_item['scenario']))
        print("Response code {resp}, expected response code {expt}"
              .format(resp=str(response_code),
                      expt=str(test_item['expected_code'])))
        print("Response json: {json}".format(json=str(response_json)))
        print("Test Result: {res}"
              .format(res='passed' if succeed else 'failed'))

    print("\nOverall Result: {res}\n"
          .format(res='PASSED' if overall_succeed else 'FAILED'))
    return overall_succeed


if __name__ == '__main__':
    if len(sys.argv) < 2:
        TESTS = [
            'reset_wrong',
            'reset',
            'update_kpi_wrong',
            'update_kpi',
            'update_gml_wrong',
            'update_gml_without_kpi',
            'update_gml',
            'train_wrong',
            'train_without_kpi',
            'train',
            'predict_wrong',
            'predict_without_train',
            'predict',
            'localize_wrong',
            'localize_without_gml',
            'localize',
            'rank',
        ]

        total = len(TESTS)
        passed = 0
        for test_case in TESTS:
            test_succeed = test(test_case)
            if test_succeed:
                passed += 1
        print("Executed {total} tests, {passed} passed"
              .format(total=total, passed=passed))
        if not passed == total:
            sys.exit(-1)
    else:
        test(sys.argv[1])
