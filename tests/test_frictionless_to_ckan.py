# coding=utf-8

import pytest

import frictionless_ckan_mapper.frictionless_to_ckan as frictionless_to_ckan


converter = frictionless_to_ckan.FrictionlessToCKAN()


class TestResourceConversion:
    pass


class TestPackageConversion:
    def test_name_title_and_version(self):
        indict = {
            'name': 'gdp',
            'title': 'Countries GDP',
            'version': '1.0',
        }
        result = converter.package(indict)
        assert result['name'] == indict['name']
        assert result['title'] == indict['title']
        assert result['version'] == indict['version']

    def test_name_is_lowercased(self):
        indict = {'name': 'ThEnAmE'}
        result = converter.package(indict)
        assert result['name'] == indict['name'].lower()