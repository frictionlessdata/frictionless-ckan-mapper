import json

import frictionless_ckan_mapper.ckan_to_frictionless as ckan_to_frictionless

import pytest

# my instinct is that more discrete tests, testing a specific part of
# conversion are better b/c that way we can see what is tested (o/w we probably
# need comments in json which is hard to do - without some hacking (e.g.
# stripping // lines before json parsing).

# TODO: copy over from test_converter all tests ...

converter = ckan_to_frictionless.CKANToFrictionless()


class TestResourceConversion:

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
        out = converter.ckan_resource_to_fd_resource(indict)
        assert out == exp

    def _test_extras_and_all_values_are_unjsonified(self, schema_json_test_cases):
        test_cases, test_file_name = schema_json_test_cases[0], schema_json_test_cases[1]
        for test_case in test_cases:
            indict = {'schema': json.dumps(test_case['test_input'])}
            out = converter.ckan_resource_to_fd_resource(indict)
            assert out == test_case['exp'], ("Error in test id "
                                             f"#{test_case['test_id']} [see {test_file_name}]")

    @pytest.mark.parametrize(
        "indict,exp",
        [
            (
                {'package_id': 'abc', 'position': 0},
                {}
            )
        ],
        ids=['package_id=abc,position=0']
    )
    def test_keys_are_removed_that_should_be(self, indict, exp):
        out = converter.ckan_resource_to_fd_resource(indict)
        assert out == exp

    @pytest.mark.parametrize(
        "indict,exp",
        [(
            {'url': 'http://www.somewhere.com/data.csv'},
            {'path': 'http://www.somewhere.com/data.csv'}
        )
        ],
        ids=['url=http://www.somewhere.com/data.csv']
    )
    def test_resource_url(self, indict, exp):
        out = converter.ckan_resource_to_fd_resource(indict)
        assert out == exp

    @pytest.mark.parametrize(
        "indict,exp",
        [
            (
                {
                    'url': 'http://www.somewhere.com/data.csv',
                    'url_type': 'upload'
                },
                {'path': 'http://www.somewhere.com/data.csv'}
            )
        ],
        ids=['url=http://www.somewhere.com/data.csv']
    )
    def test_resource_path_is_set_even_for_uploaded_resources(self, indict, exp):
        out = converter.ckan_resource_to_fd_resource(indict)
        assert out == exp

    def test_resource_description(self):
        self.resource_dict.update({
            'description': 'GDPs list',
        })
        result = converter.dataset_to_datapackage(self.dataset_dict)
        resource = result.get('resources')[0]
        assert resource.get('description') == self.resource_dict['description']

    def test_resource_format(self):
        self.resource_dict.update({
            'format': 'CSV',
        })
        result = converter.dataset_to_datapackage(self.dataset_dict)
        resource = result.get('resources')[0]
        assert resource.get('format') == self.resource_dict['format']

    def test_resource_hash(self):
        self.resource_dict.update({
            'hash': 'e785c0883d7a104330e69aee73d4f235',
        })
        result = converter.dataset_to_datapackage(self.dataset_dict)
        resource = result.get('resources')[0]
        assert resource.get('hash') == self.resource_dict['hash']

    def test_resource_schema(self):
        self.resource_dict.update({
            'schema': {
                'fields': [
                    {'name': 'id', 'type': 'integer'},
                    {'name': 'title', 'type': 'string'},
                ]
            }
        })
        result = converter.dataset_to_datapackage(self.dataset_dict)
        resource = result.get('resources')[0]
        assert resource.get('schema') == self.resource_dict['schema']

    def test_resource_schema_string(self):
        schema = {
            'fields': [
                {'name': 'id', 'type': 'integer'},
                {'name': 'title', 'type': 'string'},
            ]
        }
        self.resource_dict.update({
            'schema': json.dumps(schema)
        })
        result = converter.dataset_to_datapackage(self.dataset_dict)
        resource = result.get('resources')[0]
        assert resource.get('schema') == schema

    def test_resource_schema_url(self):
        self.resource_dict.update({
            'schema': 'http://example.com/some.schema.json'
        })
        result = converter.dataset_to_datapackage(self.dataset_dict)
        resource = result.get('resources')[0]
        assert resource.get('schema') == self.resource_dict['schema']

    def test_resource_name_lowercases_the_name(self):
        self.resource_dict.update({
            'name': 'ThE-nAmE',
        })
        expected_name = 'the-name'
        result = converter.dataset_to_datapackage(self.dataset_dict)
        resource = result.get('resources')[0]
        assert resource.get('name') == expected_name
        assert resource.get('title') == self.resource_dict['name']

    def test_resource_name_slugifies_the_name(self):
        self.resource_dict.update({
            'name': 'Lista de PIBs dos países!   51',
        })
        expected_name = 'lista-de-pibs-dos-paises-51'
        result = converter.dataset_to_datapackage(self.dataset_dict)
        resource = result.get('resources')[0]
        assert resource.get('name') == expected_name
        assert resource.get('title') == self.resource_dict['name']

    def test_resource_name_converts_unicode_characters(self):
        self.resource_dict.update({
            'name': u'万事开头难',
        })
        expected_name = 'mo-shi-kai-tou-nan'
        result = converter.dataset_to_datapackage(self.dataset_dict)
        resource = result.get('resources')[0]
        assert resource.get('name') == expected_name
        assert resource.get('title') == self.resource_dict['name']


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
        out = self.converter.dataset_to_datapackage(indict)
        assert out['license'] == license

    def test_basic_dataset_in_setup_is_valid(self):
        converter.dataset_to_datapackage(self.dataset_dict)

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

        converter.dataset_to_datapackage(valid_dataset_dict)
        with pytest.raises(KeyError):
            converter.dataset_to_datapackage(invalid_dataset_dict)

    def test_dataset_name_title_and_version(self):
        self.dataset_dict.update({
            'name': 'gdp',
            'title': 'Countries GDP',
            'version': '1.0',
        })
        result = converter.dataset_to_datapackage(self.dataset_dict)
        assert result['title'] == self.dataset_dict['title']
        assert result['name'] == self.dataset_dict['name']
        assert result['version'] == self.dataset_dict['version']

    def test_dataset_notes(self):
        self.dataset_dict.update({
            'notes': 'Country, regional and world GDP in current US Dollars.'
        })
        result = converter.dataset_to_datapackage(self.dataset_dict)
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
        result = converter.dataset_to_datapackage(self.dataset_dict)
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
        result = converter.dataset_to_datapackage(self.dataset_dict)
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
        result = converter.dataset_to_datapackage(self.dataset_dict)
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

test_dataset_maintainer -> There is no "author" in a datapackage according to the specs.
Maybe this should map to contributors?

test_dataset_ckan_url -> CKAN should now be using "url",
not "ckan_url". (?)
'''
