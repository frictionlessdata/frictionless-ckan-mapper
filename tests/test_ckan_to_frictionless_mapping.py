import unittest
import json

import ckan_datapackage_tools


def test_ckan_to_frictionless_json_conversion_resource():
    inpath = 'tests/fixtures/ckan_resource.json'
    exppath = 'tests/fixtures/frictionless_resource.json'
    converter = ckan_datapackage_tools.CKANToFrictionless()
    indict = json.load(open(inpath))
    exp = json.load(open(exppath))
    out = converter.resource(indict)
    assert out == exp
