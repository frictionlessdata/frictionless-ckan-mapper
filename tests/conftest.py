import json

import pytest

@pytest.fixture()
def schema_json_test_cases():
    '''Used to load multiple test cases for the "schema" property.'''
    list_test_cases = []
    file_name = 'tests/fixtures/schema_test_cases.json'
    with open(file_name) as test_cases:
        content = test_cases.read()
        data = json.loads(content)
    for test_case in data:
        list_test_cases.append(test_case)
    return list_test_cases, file_name