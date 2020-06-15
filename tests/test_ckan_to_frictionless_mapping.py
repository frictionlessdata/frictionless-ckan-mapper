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

# my instinct is that more discrete tests, testing a specific part of
# conversion are better b/c that way we can see what is tested (o/w we probably
# need comments in json which is hard to do - without some hacking (e.g.
# stripping // lines before json parsing).

# TODO: copy over from test_converter all tests ...

# TODO parametrize ...

class TestPackageConversion:
    def test_delete_keys(self):
        pass
    
    def test_author_and_maintainer(self):
        pass
