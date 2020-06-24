# coding=utf-8

import pytest

import frictionless_ckan_mapper.frictionless_to_ckan as frictionless_to_ckan


converter = frictionless_to_ckan.FrictionlessToCKAN()


class TestResourceConversion:
    pass


class TestPackageConversion:
    def test_passthrough(self):
        indict = {
            'name': 'gdp',
            'title': 'Countries GDP',
            'version': '1.0',
        }
        result = converter.package(indict)
        assert result['name'] == indict['name']
        assert result['title'] == indict['title']
        assert result['version'] == indict['version']

    def test_description_is_converted_to_notes(self):
        indict = {
            'description': 'Country, regional and world GDP in current USD.'
        }
        result = converter.package(indict)
        assert result.get('notes') == indict['description']

    # TODO: make sure that we deal with the 'path' property too
    # coming from Frictionless. The 'type' property is not expected
    # according to the specs (this test is adapted from an existing test):
    # https://specs.frictionlessdata.io/data-package/#metadata
    # "The object MUST contain a name property and/or a path property.
    # It MAY contain a title property."
    def test_dataset_license(self):
        indict = {
            'licenses': [{
                'type': 'odc-odbl'
            }]
        }
        exp = {
            'license_id': 'odc-odbl'
        }
        out = converter.package(indict)
        assert out == exp

        indict = {
            'licenses': [{
                'title': 'Open Data Commons Open Database License',
                'type': 'odc-odbl'
            }]
        }
        exp = {
            'license_id': 'odc-odbl',
            'license_title': 'Open Data Commons Open Database License'
        }
        out = converter.package(indict)
        assert out == exp

        # Finally, what if license*s* are already there...
        indict = {
            'licenses': [
                {
                    'title': 'Open Data Commons Open Database License',
                    'type': 'odc-pddl'
                },
                {
                    'title': 'Creative Commons CC Zero License (cc-zero)',
                    'type': 'cc-zero'
                }
            ]
        }
        exp = {
            'extras': [{
                'licenses': indict['licenses']
            }],
            'license_id': 'odc-pddl',
            'license_title': 'Open Data Commons Open Database License',
        }
        out = converter.package(indict)
        assert out == exp
