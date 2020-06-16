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

    def _test_fixtures(self):
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
            "url_type": "file"
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
            'path': 'http://www.somewhere.com/data.csv'
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

    def test_resource_name_slugifies_the_name_and_adds_title(self):
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

    def test_delete_keys(self):
        pass

    def test_author_and_maintainer(self):
        pass

    def _test_dataset_license(self):
        license = {
            'type': 'cc-zero',
            'title': 'Creative Commons CC Zero License (cc-zero)',
            'url': 'http://opendefinition.org/licenses/cc-zero/'
        }
        indict = {
            'license_id': license['type'],
            'license_title': license['title'],
            'license_url': license['url'],
        }
        out = self.converter.dataset(indict)
        assert out['license'] == license

    def test_basic_dataset_in_setup_is_valid(self):
        converter.dataset(self.dataset_dict)

    def test_dataset_only_requires_a_name_to_be_valid(self):
        invalid_dataset_dict = {}
        valid_dataset_dict = {
            'name': 'gdp',
            'resources': [
                {
                    'name': 'the-resource',
                }
            ]

        }

        converter.dataset(valid_dataset_dict)
        with pytest.raises(KeyError):
            converter.dataset(invalid_dataset_dict)

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


'''
# TODO: Add following tests:

test_dataset_license -> This is different from the current specs:
The test expects `license` as a dict, but the specs expect a list of licenses:
    licenses: [
        license1: {},
        license2: {}
    ]
https://specs.frictionlessdata.io/schemas/data-package.json

test_dataset_maintainer -> There is no "author" in a datapackage according to
the specs.  Maybe this should map to contributors?

test_dataset_ckan_url -> CKAN should now be using "url",
not "ckan_url". (?)
'''
