# coding=utf-8

import json

import pytest

import frictionless_ckan_mapper.ckan_to_frictionless as ckan_to_frictionless


converter = ckan_to_frictionless.CKANToFrictionless()


class TestResourceConversion:
    '''Notes:

    * extras do not any special testing since CKAN already just has them as key
      values.
    * we do want to test unjsonifying values since that will cover e.g. a Table
      Schema set in schema field
    '''

    def test_fixtures(self):
        inpath = 'tests/fixtures/ckan_resource.json'
        exppath = 'tests/fixtures/frictionless_resource.json'
        converter = ckan_to_frictionless.CKANToFrictionless()
        indict = json.load(open(inpath))
        exp = json.load(open(exppath))
        out = converter.resource(indict)
        assert out == exp

    def test_values_are_unjsonified(self):
        '''Test values which are jsonified dict or arrays are unjsonified'''
        schema = {
            "fields": [
                { "name": "abc", "type": "string" }
            ]
        }
        indict = {
            "schema": json.dumps(schema),
            "otherval": json.dumps(schema),
            "x": "{'abc': 1"
        }
        exp = {
            "schema": schema,
            "otherval": schema,
            # fake json object - not really ... but looks like it ...
            "x": "{'abc': 1"
        }
        out = converter.resource(indict)
        assert out == exp

        indict = {
            "x": "hello world",
            "y": "1.3"
            }
        exp = {
            "x": "hello world",
            "y": "1.3"
            }
        out = converter.resource(indict)
        assert out == exp

    def test_keys_are_removed_that_should_be(self):
        indict = {
            "package_id": "xxx",
            "position": 2,
            "datastore_active": True,
            "state": "active"
        }
        exp = {}
        out = converter.resource(indict)
        assert out == exp

    def test_resource_url(self):
        indict = {
            "url": "http://www.somewhere.com/data.csv"
            }
        exp = {
            "path": "http://www.somewhere.com/data.csv"
            }
        out = converter.resource(indict)
        assert out == exp

    def test_resource_path_is_set_even_for_uploaded_resources(self):
        indict = {
            "url": "http://www.somewhere.com/data.csv",
            "url_type": "upload"
        }
        exp = {
            'path': 'http://www.somewhere.com/data.csv',
            'url_type': "upload"
        }
        out = converter.resource(indict)
        assert out == exp

    def test_resource_keys_pass_through(self):
        indict = {
            'description': 'GDPs list',
            'format': 'CSV',
            'hash': 'e785c0883d7a104330e69aee73d4f235',
            'schema': {
                'fields': [
                    {'name': 'id', 'type': 'integer'},
                    {'name': 'title', 'type': 'string'},
                ]
            },
            # random
            'adfajka': 'aaaa',
            '1dafak': 'abbbb'
        }
        exp = indict
        out = converter.resource(indict)
        assert out == exp

    # TODO: remove sluggification (if needed make it part of strict mode)
    def test_resource_name_slugifies_the_name(self):
        indict = {
            'name': 'ThE-nAmE'
        }
        exp = {
            'name': 'the-name'
        }
        out = converter.resource(indict)
        assert out == exp

        indict = {
            'name': 'Lista de PIBs dos países!   51'
        }
        exp = {
            'name': 'lista-de-pibs-dos-paises-51'
        }
        out = converter.resource(indict)
        assert out == exp

    def test_resource_name_converts_unicode_characters(self):
        indict = {
            'name': u'万事开头难'
        }
        exp = {
            'name': 'mo-shi-kai-tou-nan'
        }
        out = converter.resource(indict)
        assert out == exp

    def test_nulls_are_stripped(self):
        indict = {
            'abc': 'xxx',
            'size': None,
            'xyz': None
        }
        exp = {
            'abc': 'xxx'
        }
        out = converter.resource(indict)
        assert out == exp


class TestPackageConversion:
    @classmethod
    def setup_class(self):
        self.converter = ckan_to_frictionless.CKANToFrictionless()

        self.resource_dict = {
            'id': '1234',
            'name': 'data.csv',
            'url': 'http://someplace.com/data.csv'
        }
        self.dataset_dict = {
            'name': 'gdp',
            'title': 'Countries GDP',
            'version': '1.0',
            'resources': [self.resource_dict],
        }

    def test_author_and_maintainer(self):
        pass

    def test_dataset_license(self):
        indict = {
            'license_id': 'odc-odbl',
            # TODO: check package_show in CKAN
            # 'license_title': 'Open Data Commons Open Database License',
            # 'license_url': 'http://opendefinition.org/licenses/odc-odbl/'
        }
        exp = {
            "licenses": [{
                'type': 'odc-odbl',
            }]
        }
        out = converter.dataset(indict)
        assert out == exp

    def test_dataset_name_title_and_version(self):
        self.dataset_dict.update({
            'name': 'gdp',
            'title': 'Countries GDP',
            'version': '1.0',
        })
        result = converter.dataset(self.dataset_dict)
        assert result['title'] == self.dataset_dict['title']
        assert result['name'] == self.dataset_dict['name']
        assert result['version'] == self.dataset_dict['version']

    def test_dataset_notes(self):
        self.dataset_dict.update({
            'notes': 'Country, regional and world GDP in current US Dollars.'
        })
        result = converter.dataset(self.dataset_dict)
        assert result.get('description') == self.dataset_dict['notes']

    def test_dataset_author_and_source(self):
        sources = [
            {
                'title': 'World Bank and OECD',
                'email': 'someone@worldbank.org',
                'path': 'http://data.worldbank.org/indicator/NY.GDP.MKTP.CD',
            }
        ]
        self.dataset_dict.update({
            'author': sources[0]['title'],
            'author_email': sources[0]['email'],
            'url': sources[0]['path']
        })
        result = converter.dataset(self.dataset_dict)
        assert result.get('sources') == sources

    def test_dataset_tags(self):
        keywords = [
            'economy', 'worldbank'
        ]
        self.dataset_dict.update({
            'tags': [
                {
                    'display_name': 'economy',
                    'id': '9d602a79-7742-44a7-9029-50b9eca38c90',
                    'name': 'economy',
                    'state': 'active'
                },
                {
                    'display_name': 'worldbank',
                    'id': '3ccc2e3b-f875-49ef-a39d-6601d6c0ef76',
                    'name': 'worldbank',
                    'state': 'active'
                }
            ]
        })
        result = converter.dataset(self.dataset_dict)
        assert result.get('keywords') == keywords

    def test_dataset_extras(self):
        self.dataset_dict.update({
            'extras': [
                {'key': 'title_cn', 'value': u'國內生產總值'},
                {'key': 'years', 'value': '[2015, 2016]'},
                {'key': 'last_year', 'value': 2016},
                {'key': 'location', 'value': '{"country": "China"}'},
            ]
        })
        result = converter.dataset(self.dataset_dict)
        assert result.get('extras') == {
            'title_cn': u'國內生產總值',
            'years': [2015, 2016],
            'last_year': 2016,
            'location': {'country': 'China'},
        }

    def test_unjsonify_all_extra_values_in_nested_dicts(self):
        self.dataset_dict.update({
            'extras': [
                {
                    'key': 'location',
                    'value': ('{"country": {"China": {"population": '
                              '"1233214331", "capital": "Beijing"}}}')
                }
            ]
        })
        out = converter.dataset(self.dataset_dict)
        exp = {'location':
               {'country':
                {'China': {'population': '1233214331',
                           'capital': 'Beijing'}}
                }
               }
        assert out.get('extras') == exp

    def test_unjsonify_all_extra_values_in_nested_lists(self):
        self.dataset_dict.update({
            'extras': [
                {
                    'key': 'numbers',
                    'value': '[[[1, 2, 3], [2, 4, 5]], [[7, 6, 0]]]'
                }
            ]
        })
        out = converter.dataset(self.dataset_dict)
        exp = {'numbers': [[[1, 2, 3], [2, 4, 5]], [[7, 6, 0]]]}
        assert out.get('extras') == exp

    def test_unjsonify_all_extra_values_in_nested_mixed_types(self):
        self.dataset_dict.update({
            'extras': [
                {
                    'key': 'numbers',
                    'value': ('{"lists": [[[1, 2, 3],'
                    '{"total": 3, "nums": [3,4]}], [[7, 6, 0]]]}'
                    )
                }
            ]
        })
        out = converter.dataset(self.dataset_dict)
        exp = {'numbers':
               {"lists":
                [[[1, 2, 3], {"total": 3, "nums": [3, 4]}], [[7, 6, 0]]]}
               }
        assert out.get('extras') == exp

    def test_resources_are_converted(self):
        # Package has multiple resources
        new_resource = {
            'id': '12345',
            'name': 'data2.csv',
            'url': 'http://someotherplace.com/data2.csv'
        }
        indict = {
            'name': 'gdp',
            'title': 'Countries GDP',
            'resources': [self.resource_dict, new_resource],
        }
        result = converter.dataset(indict)
        assert len(result['resources']) == 2

        # Package has a single resource
        result = converter.dataset(self.dataset_dict)
        assert len(result['resources']) == 1

    # TODO: CKAN object does not necessarily have `resources` (optional)
    # Frictionless object MUST have a `resources` property.
    # Should the implementation raise an error as the datapackage
    # would not be valid without at least one resource?
    def _test_empty_resources_raise_error(self):
        pass

    def test_keys_are_removed_that_should_be(self):
        indict = {
            'state': 'active'
        }
        exp = {
        }
        out = converter.dataset(indict)
        assert out == exp