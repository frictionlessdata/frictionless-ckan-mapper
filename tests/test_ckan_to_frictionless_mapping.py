import json

import frictionless_ckan_mapper.ckan_to_frictionless as ckan_to_frictionless


def test_resource():
    inpath = 'tests/fixtures/ckan_resource.json'
    exppath = 'tests/fixtures/frictionless_resource.json'
    converter = ckan_to_frictionless.CKANToFrictionless()
    indict = json.load(open(inpath))
    exp = json.load(open(exppath))
    out = converter.resource(indict)
    assert out == exp


def test_package():
    inpath = 'tests/fixtures/ckan_package.json'
    exppath = 'tests/fixtures/frictionless_package.json'
    converter = ckan_to_frictionless.CKANToFrictionless()
    indict = json.load(open(inpath))
    exp = json.load(open(exppath))
    out = converter.package(indict)
    assert out == exp
