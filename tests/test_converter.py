# -*- coding: utf-8 -*-

import unittest
import json

import datapackage
import ckan_datapackage_tools.converter as converter

import requests_mock
import six


class TestConvertToDict(unittest.TestCase):

    def setUp(self):
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
            'organization': {
                'title': 'World Bank',
                'name': 'World Bank and OECD',
                'is_organization': True
            }
        }

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
            ],
            'organization': {
                'title': 'World Bank',
                'name': 'World Bank and OECD'
            }

        }

        converter.dataset_to_datapackage(valid_dataset_dict)
        with self.assertRaises(KeyError):
            converter.dataset_to_datapackage(invalid_dataset_dict)

    def test_dataset_name_title_and_version(self):
        self.dataset_dict.update({
            'name': 'gdp',
            'title': 'Countries GDP',
            'version': '1.0',
        })
        result = converter.dataset_to_datapackage(self.dataset_dict)
        self.assertEquals(result['title'], self.dataset_dict['title'])
        self.assertEquals(result['name'], self.dataset_dict['name'])
        self.assertEquals(result['version'], self.dataset_dict['version'])

    def test_dataset_notes(self):
        self.dataset_dict.update({
            'notes': 'Country, regional and world GDP in current US Dollars.'
        })
        result = converter.dataset_to_datapackage(self.dataset_dict)
        self.assertEquals(result.get('description'),
                          self.dataset_dict['notes'])

    def test_dataset_license(self):
        license = {
            'type': 'cc-zero',
            'title': 'Creative Commons CC Zero License (cc-zero)',
            'url': 'http://opendefinition.org/licenses/cc-zero/'
        }
        self.dataset_dict.update({
            'license_id': license['type'],
            'license_title': license['title'],
            'license_url': license['url'],
        })
        result = converter.dataset_to_datapackage(self.dataset_dict)

        self.assertEquals(result.get('licenses'), [{
            'name': 'cc-zero',
            'title': 'Creative Commons CC Zero License (cc-zero)',
            'path': 'http://opendefinition.org/licenses/cc-zero/'
        }])
        self.assertEquals(result.get('license'), None)

    def test_dataset_license_and_licenses_as_extras(self):
        primary_license = {
            'license_id': 'cc-zero',
            'license_title': 'Creative Commons CC Zero License (cc-zero)',
            'license_url': 'http://opendefinition.org/licenses/cc-zero/'
        }
        extra_licenses = [{
            'type': 'cc-by-sa',
            'title': 'Creative Commons Attribution Share-Alike (cc-by-sa)',
            'url': 'http://www.opendefinition.org/licenses/cc-by-sa/'
        }]
        self.dataset_dict.update(primary_license)
        self.dataset_dict.update({
            'extras': [{
                'key':'licenses',
                'value': extra_licenses
             }]
        })
        result = converter.dataset_to_datapackage(self.dataset_dict)
        self.assertEquals(result.get('licenses'), [{
            'name': 'cc-zero',
            'title': 'Creative Commons CC Zero License (cc-zero)',
            'path': 'http://opendefinition.org/licenses/cc-zero/'
        },
        {
            'name': 'cc-by-sa',
            'title': 'Creative Commons Attribution Share-Alike (cc-by-sa)',
            'path': 'http://www.opendefinition.org/licenses/cc-by-sa/'
         }
        ])
        self.assertEquals(result.get('license'), None)

    def test_dataset_author_and_source(self):
        sources = [{
                "author": "someone",
                "title": "World Bank and OECD Data",
                "author_email": "someone@worldbank.org",
                "url": "http://data.worldbank.org/indicator/NY.GDP.MKTP.CD"
            },
            {
                "url": "http://data.worldbank.org/indicator/NY.GDP.MKTP.CD2"
            },
            {
                "title": "World Bank and OECD Data",
                "url": "http://data.worldbank.org/indicator/NY.GDP.MKTP.CD3"
            },
            {
                "title": "World Bank and OECD",
                "path": "http://data.worldbank.org/indicator/NY.GDP.MKTP.CD4"
            },
            {},
            {
                "author_email": "someone6@worldbank.org",
            },
            {
                "url": "http://data.worldbank.org/indicator/NY.GDP.MKTP.CD7"
            },
            ]
        expected_results = [
            [{
                "title": "World Bank and OECD",
                "path": "http://data.worldbank.org/indicator/NY.GDP.MKTP.CD"
            }],
            [{
                "title": "World Bank and OECD",
                "path": "http://data.worldbank.org/indicator/NY.GDP.MKTP.CD2"
            }],
            [{
                "title": "World Bank and OECD",
                "path": "http://data.worldbank.org/indicator/NY.GDP.MKTP.CD3"
            }],
            [{
                "title": "World Bank and OECD"
            }],
            [{
                "title": "World Bank and OECD",
            }],
            [{
                "title": "World Bank and OECD",
            }],
            [{
                "title": "World Bank and OECD",
                "path": "http://data.worldbank.org/indicator/NY.GDP.MKTP.CD7"
            }],
        ]
        for source, expected_result in zip(sources, expected_results):
            self.dataset_dict = {
                'name': 'gdp',
                'title': 'Countries GDP',
                'version': '1.0',
                'resources': [self.resource_dict],
                'organization': {
                    'title': 'World Bank',
                    'name': 'World Bank and OECD',
                    'is_organization': True
                }
            }
            self.dataset_dict.update(source)
            result = converter.dataset_to_datapackage(self.dataset_dict)
            self.assertEquals(result['sources'], expected_result)
            self.assertEquals(result.get('source'), None)

    def test_organisation_as_source_and_extra_sources(self):
        extra_sources = [{
            'name': 'source1',
            'email': 'source1@test.com',
            'url': 'http://source1.com'
        },
        {
            'title': 'source2',
            'email': 'source2@test.com',
            'path': 'http://source2.com'
        }]
        self.dataset_dict.update({
            'url' : 'http://worldbankandoecd.com'
        })
        self.dataset_dict.update({
            'extras': [{
                'key': 'sources',
                'value': extra_sources
            }]
        })
        result = converter.dataset_to_datapackage(self.dataset_dict)
        self.assertEquals(result.get('sources'), [
            {
                'title': 'World Bank and OECD',
                'path': 'http://worldbankandoecd.com'
            },
            {
                'title': 'source1',
                'email': 'source1@test.com',
                'path': 'http://source1.com'
            },
            {
                'title': 'source2',
                'email': 'source2@test.com',
                'path': 'http://source2.com'
            }
        ])
        self.assertEquals(result.get('source'), None)

    def test_dataset_author_as_contributor(self):
        self.dataset_dict.update({
            'author': 'John Smith',
            'author_email': 'jsmith@email.com'
        })
        expected_result = [
            {
                'title': 'John Smith',
                'email': 'jsmith@email.com',
                'role': 'author'
            }
        ]
        result = converter.dataset_to_datapackage(self.dataset_dict)
        self.assertEquals(result.get('contributors'), expected_result)
        self.assertEquals(result.get('author'), None)
        self.assertEquals(result.get('maintainer'), None)

    def test_dataset_maintainer(self):
        author = {
            'name': 'John Smith',
            'email': 'jsmith@email.com'
        }
        self.dataset_dict.update({
            'maintainer': author['name'],
            'maintainer_email': author['email'],
        })
        expected_result = [
            {
                'title': 'John Smith',
                'email': 'jsmith@email.com',
                'role': 'maintainer'
            }
        ]
        result = converter.dataset_to_datapackage(self.dataset_dict)
        self.assertEquals(result.get('contributors'), expected_result)
        self.assertEquals(result.get('author'), None)
        self.assertEquals(result.get('maintainer'), None)

    def test_dataset_maintainer_and_author_and_extras_as_contributors(self):
        author = {
            'author': 'John Smith',
            'author_email': 'jsmith@email.com',
        }
        maintainer = {
            'maintainer': 'Jane Smith',
            'maintainer_email': 'janesmith@email.com',
        }
        extras = [{
            'title': 'Bob Smith',
            'role': 'publisher',
            'path': 'http://bobsmith.com'
        },
        {
            'name': 'Peter Invalid Smith',
            'email': 'petersmith@email.com',
            'role': 'maintainer'
        },
        {
            'email': 'noTitle@email.com',
            'role': 'contributor'
        },
        {
            'title': 'Jo Smith',
            'organization': 'org1'
        },
        {
            'title': 'Sam Smith',
        }]
        self.dataset_dict.update(author)
        self.dataset_dict.update(maintainer)
        self.dataset_dict.update({
            'extras': [{
                'key': 'contributors',
                'value': extras
            }]
        })
        result = converter.dataset_to_datapackage(self.dataset_dict)
        log.info('contributors result %r', result.get('contributors'))
        self.assertEquals(result.get('contributors'), [
            {
                'title': 'John Smith',
                'email': 'jsmith@email.com',
                'role': 'author'
            },
            {
                'title': 'Jane Smith',
                'email': 'janesmith@email.com',
                'role': 'maintainer'
            },
            {
                'title': 'Bob Smith',
                'role': 'publisher',
                'path': 'http://bobsmith.com'
            },
            {
                'title': 'Jo Smith',
                'organization': 'org1'
            },
            {
                'title': 'Sam Smith'
            }
        ])
        self.assertEquals(result.get('maintainer'), None)
        self.assertEquals(result.get('author'), None)

    def test_dataset_author_as_contributor_and_source(self):
        self.dataset_dict.update({
            'author': 'John Smith',
            'author_email': 'jsmith@email.com',
            'url': 'http://data.worldbank.org/indicator/NY.GDP.MKTP.CD'
        })
        expected_sources = [{
            "title": "World Bank and OECD",
            "path": "http://data.worldbank.org/indicator/NY.GDP.MKTP.CD"
        }]
        expected_contributors = [{
            'title': 'John Smith',
            'email': 'jsmith@email.com',
            'role': 'author'
        }]
        result = converter.dataset_to_datapackage(self.dataset_dict)
        self.assertEquals(result['sources'], expected_sources)
        self.assertEquals(result['contributors'], expected_contributors)

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
        self.assertEquals(result.get('keywords'), keywords)

    def test_dataset_ckan_url(self):
        self.dataset_dict.update({
            'ckan_url': 'http://www.somewhere.com/datasets/foo'
        })
        result = converter.dataset_to_datapackage(self.dataset_dict)
        self.assertEquals(result.get('homepage'),
                          self.dataset_dict['ckan_url'])

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
        self.assertEqual(result.get('extras'), {
            'title_cn': u'國內生產總值',
            'years': [2015, 2016],
            'last_year': 2016,
            'location': {'country': 'China'},
        })

    def test_resource_url(self):
        self.resource_dict.update({
            'url': 'http://www.somewhere.com/data.csv',
        })
        result = converter.dataset_to_datapackage(self.dataset_dict)
        resource = result.get('resources')[0]
        self.assertEquals(resource.get('path'),
                          self.resource_dict['url'])

    def test_resource_path_is_set_even_for_uploaded_resources(self):
        self.resource_dict.update({
            'id': 'foo',
            'url': 'http://www.somewhere.com/data.csv',
            'url_type': 'upload',
        })
        result = converter.dataset_to_datapackage(self.dataset_dict)
        resource = result.get('resources')[0]
        self.assertEquals(resource.get('path'),
                          self.resource_dict['url'])

    def test_resource_description(self):
        self.resource_dict.update({
            'description': 'GDPs list',
        })
        result = converter.dataset_to_datapackage(self.dataset_dict)
        resource = result.get('resources')[0]
        self.assertEquals(resource.get('description'),
                          self.resource_dict['description'])

    def test_resource_format(self):
        self.resource_dict.update({
            'format': 'CSV',
        })
        result = converter.dataset_to_datapackage(self.dataset_dict)
        resource = result.get('resources')[0]
        self.assertEquals(resource.get('format'),
                          self.resource_dict['format'])

    def test_resource_hash(self):
        self.resource_dict.update({
            'hash': 'e785c0883d7a104330e69aee73d4f235',
        })
        result = converter.dataset_to_datapackage(self.dataset_dict)
        resource = result.get('resources')[0]
        self.assertEquals(resource.get('hash'),
                          self.resource_dict['hash'])

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
        self.assertEquals(resource.get('schema'),
                          self.resource_dict['schema'])

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
        self.assertEquals(resource.get('schema'),
                          schema)

    def test_resource_schema_url(self):
        self.resource_dict.update({
            'schema': 'http://example.com/some.schema.json'
        })
        result = converter.dataset_to_datapackage(self.dataset_dict)
        resource = result.get('resources')[0]
        self.assertEquals(resource.get('schema'),
                          self.resource_dict['schema'])

    def test_resource_name_lowercases_the_name(self):
        self.resource_dict.update({
            'name': 'ThE-nAmE',
        })
        expected_name = 'the-name'
        result = converter.dataset_to_datapackage(self.dataset_dict)
        resource = result.get('resources')[0]
        self.assertEquals(resource.get('name'), expected_name)
        self.assertEquals(resource.get('title'),
                          self.resource_dict['name'])

    def test_resource_name_slugifies_the_name(self):
        self.resource_dict.update({
            'name': 'Lista de PIBs dos países!   51',
        })
        expected_name = 'lista-de-pibs-dos-paises-51'
        result = converter.dataset_to_datapackage(self.dataset_dict)
        resource = result.get('resources')[0]
        self.assertEquals(resource.get('name'), expected_name)
        self.assertEquals(resource.get('title'),
                          self.resource_dict['name'])

    def test_resource_name_converts_unicode_characters(self):
        self.resource_dict.update({
            'name': u'万事开头难',
        })
        expected_name = 'mo-shi-kai-tou-nan'
        result = converter.dataset_to_datapackage(self.dataset_dict)
        resource = result.get('resources')[0]
        self.assertEquals(resource.get('name'), expected_name)
        self.assertEquals(resource.get('title'),
                          self.resource_dict['name'])


class TestDataPackageToDatasetDict(unittest.TestCase):
    def setUp(self):
        datapackage_dict = {
            'name': 'gdp',
            'title': 'Countries GDP',
            'version': '1.0',
            'resources': [
                {
                    'name': 'datetimes.csv',
                    'path': 'test-data/datetimes.csv'
                }
            ],
        }

        self.datapackage = datapackage.DataPackage(datapackage_dict)

    def test_basic_datapackage_in_setup_is_valid(self):
        converter.datapackage_to_dataset(self.datapackage)

    def test_datapackage_only_requires_some_fields_to_be_valid(self):
        invalid_datapackage = datapackage.DataPackage({})
        valid_datapackage = datapackage.DataPackage({
            'name': 'gdp',
            'resources': [
                {
                    'name': 'the-resource',
                    'path': 'http://example.com/some-data.csv'
                }
            ]
        })

        converter.datapackage_to_dataset(valid_datapackage)

        with self.assertRaises(KeyError):
            converter.datapackage_to_dataset(invalid_datapackage)

    def test_datapackage_name_title_and_version(self):
        self.datapackage.descriptor.update({
            'name': 'gdp',
            'title': 'Countries GDP',
            'version': '1.0',
        })
        result = converter.datapackage_to_dataset(self.datapackage)
        self.assertEquals(result['name'], self.datapackage.descriptor['name'])
        self.assertEquals(result['title'],
                          self.datapackage.descriptor['title'])
        self.assertEquals(result['version'],
                          self.datapackage.descriptor['version'])

    def test_name_is_lowercased(self):
        self.datapackage.descriptor.update({
            'name': 'ThEnAmE',
        })
        result = converter.datapackage_to_dataset(self.datapackage)
        self.assertEquals(result['name'],
                          self.datapackage.descriptor['name'].lower())

    def test_datapackage_description(self):
        self.datapackage.descriptor.update({
            'description': 'Country, regional and world GDP in current USD.'
        })
        result = converter.datapackage_to_dataset(self.datapackage)
        self.assertEquals(result.get('notes'),
                          self.datapackage.descriptor['description'])

    def test_datapackage_license_as_string(self):
        self.datapackage.descriptor.update({
            'license': 'cc-zero'
        })
        result = converter.datapackage_to_dataset(self.datapackage)
        self.assertEquals(result.get('license_id'), 'cc-zero')

    def test_datapackage_license_as_unicode(self):
        self.datapackage.descriptor.update({
            'license': u'cc-zero'
        })
        result = converter.datapackage_to_dataset(self.datapackage)
        self.assertEquals(result.get('license_id'), 'cc-zero')

    def test_datapackage_license_as_dict(self):
        license = {
            'type': 'cc-zero',
            'title': 'Creative Commons CC Zero License (cc-zero)',
            'url': 'http://opendefinition.org/licenses/cc-zero/'
        }
        self.datapackage.descriptor.update({
            'license': license
        })
        result = converter.datapackage_to_dataset(self.datapackage)
        self.assertEquals(result.get('license_id'), license['type'])
        self.assertEquals(result.get('license_title'), license['title'])
        self.assertEquals(result.get('license_url'), license['url'])

    def test_datapackage_sources(self):
        sources = [
            {
                'name': 'World Bank and OECD',
                'email': 'someone@worldbank.org',
                'web': 'http://data.worldbank.org/indicator/NY.GDP.MKTP.CD',
            }
        ]
        self.datapackage.descriptor.update({
            'sources': sources
        })
        result = converter.datapackage_to_dataset(self.datapackage)
        self.assertEquals(result.get('author'), sources[0]['name'])
        self.assertEquals(result.get('author_email'), sources[0]['email'])
        self.assertEquals(result.get('url'), sources[0]['web'])

    def test_datapackage_author_as_string(self):
        # FIXME: Add author.web
        author = {
            'name': 'John Smith',
            'email': 'jsmith@email.com'
        }
        self.datapackage.descriptor.update({
            'author': '{name} <{email}>'.format(name=author['name'],
                                                email=author['email'])
        })
        result = converter.datapackage_to_dataset(self.datapackage)
        self.assertEquals(result.get('maintainer'), author['name'])
        self.assertEquals(result.get('maintainer_email'), author['email'])

    def test_datapackage_author_as_unicode(self):
        # FIXME: Add author.web
        author = {
            'name': u'John Smith',
        }
        self.datapackage.descriptor.update({
            'author': author['name'],
        })
        result = converter.datapackage_to_dataset(self.datapackage)
        self.assertEquals(result.get('maintainer'), author['name'])

    def test_datapackage_author_as_string_without_email(self):
        # FIXME: Add author.web
        author = {
            'name': 'John Smith'
        }
        self.datapackage.descriptor.update({
            'author': author['name']
        })
        result = converter.datapackage_to_dataset(self.datapackage)
        self.assertEquals(result.get('maintainer'), author['name'])

    def test_datapackage_author_as_dict(self):
        # FIXME: Add author.web
        author = {
            'name': 'John Smith',
            'email': 'jsmith@email.com'
        }
        self.datapackage.descriptor.update({
            'author': author
        })
        result = converter.datapackage_to_dataset(self.datapackage)
        self.assertEquals(result.get('maintainer'), author['name'])
        self.assertEquals(result.get('maintainer_email'), author['email'])

    def test_datapackage_keywords(self):
        keywords = [
            'economy!!!', 'world bank',
        ]
        self.datapackage.descriptor.update({
            'keywords': keywords
        })
        result = converter.datapackage_to_dataset(self.datapackage)
        self.assertEquals(result.get('tags'), [
            {'name': 'economy'},
            {'name': 'world-bank'},
        ])

    def test_datapackage_extras(self):
        self.datapackage.descriptor.update({
            'title_cn': u'國內生產總值',
            'years': [2015, 2016],
            'last_year': 2016,
            'location': {'country': 'China'},
        })
        result = converter.datapackage_to_dataset(self.datapackage)

        if six.PY2:
            assertItemsEqual = self.assertItemsEqual
        elif six.PY3:
            assertItemsEqual = self.assertCountEqual

        assertItemsEqual(result.get('extras'), [
            {'key': 'profile', 'value': u'data-package'},
            {'key': 'title_cn', 'value': u'國內生產總值'},
            {'key': 'years', 'value': '[2015, 2016]'},
            {'key': 'last_year', 'value': 2016},
            {'key': 'location', 'value': '{"country": "China"}'},
        ])

    def test_resource_name_is_used_if_theres_no_title(self):
        resource = {
            'name': 'gdp',
            'title': None,
        }
        self.datapackage.resources[0].descriptor.update(resource)
        result = converter.datapackage_to_dataset(self.datapackage)
        resource = result.get('resources')[0]
        self.assertEquals(result.get('resources')[0].get('name'),
                          resource['name'])

    def test_resource_title_is_used_as_name(self):
        resource = {
            'name': 'gdp',
            'title': 'Gross domestic product',
        }

        self.datapackage.resources[0].descriptor.update(resource)
        result = converter.datapackage_to_dataset(self.datapackage)
        self.assertEquals(result.get('resources')[0].get('name'),
                          resource['title'])

    @requests_mock.Mocker(real_http=True)
    def test_resource_url(self, mock_requests):
        url = 'http://www.somewhere.com/data.csv'
        datapackage_dict = {
            'name': 'gdp',
            'title': 'Countries GDP',
            'version': '1.0',
            'resources': [
                {'path': url}
            ],
        }
        mock_requests.register_uri('GET', url, body='')

        dp = datapackage.DataPackage(datapackage_dict)
        result = converter.datapackage_to_dataset(dp)
        self.assertEquals(result.get('resources')[0].get('url'),
                          datapackage_dict['resources'][0]['path'])

    @requests_mock.Mocker(real_http=True)
    def test_resource_url_is_set_to_its_remote_data_path(self, mock_requests):
        url = 'http://www.somewhere.com/data.csv'
        datapackage_dict = {
            'name': 'gdp',
            'title': 'Countries GDP',
            'version': '1.0',
            'resources': [
                {'path': 'data.csv'}
            ],
        }
        mock_requests.register_uri('GET', url, body='')
        dp = datapackage.DataPackage(
            datapackage_dict, base_path='http://www.somewhere.com')
        result = converter.datapackage_to_dataset(dp)
        self.assertEquals(result.get('resources')[0].get('url'),
                          dp.resources[0].source)

    def test_resource_description(self):
        resource = {
            'description': 'GDPs list'
        }

        self.datapackage.resources[0].descriptor.update(resource)
        result = converter.datapackage_to_dataset(self.datapackage)
        self.assertEquals(result.get('resources')[0].get('description'),
                          resource['description'])

    def test_resource_format(self):
        resource = {
            'format': 'CSV',
        }

        self.datapackage.resources[0].descriptor.update(resource)
        result = converter.datapackage_to_dataset(self.datapackage)
        self.assertEquals(result.get('resources')[0].get('format'),
                          resource['format'])

    def test_resource_hash(self):
        resource = {
            'hash': 'e785c0883d7a104330e69aee73d4f235',
        }

        self.datapackage.resources[0].descriptor.update(resource)
        result = converter.datapackage_to_dataset(self.datapackage)
        self.assertEquals(result.get('resources')[0].get('hash'),
                          resource['hash'])

    def test_resource_schema(self):
        schema = {
            'fields': [
                {'name': 'id', 'type': 'integer'},
                {'name': 'title', 'type': 'string'},
            ]
        }
        resource = {
            'schema': schema
        }

        self.datapackage.resources[0].descriptor.update(resource)
        result = converter.datapackage_to_dataset(self.datapackage)
        self.assertEquals(result.get('resources')[0].get('schema'),
                          resource['schema'])

    def test_resource_path_is_set_to_its_local_data_path(self):
        resource = {
            'path': 'test-data/datetimes.csv',
        }
        dp = datapackage.DataPackage({
            'name': 'datetimes',
            'resources': [resource],
        })

        result = converter.datapackage_to_dataset(dp)
        self.assertEquals(result.get('resources')[0].get('path'),
                          dp.resources[0].source)
