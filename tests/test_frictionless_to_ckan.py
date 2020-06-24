# coding=utf-8

import pytest

import frictionless_ckan_mapper.frictionless_to_ckan as converter


class TestResourceConversion:
    def test_extras(self):
        indict = {
            'extras': {
                'title_cn': u'國內生產總值',
                'years': [2015, 2016],
                'last_year': 2016,
                'location': {'country': 'China'}
            }
        }
        out = converter.resource(indict)
        exp = {
            'extras': [
                {'key': 'title_cn', 'value': u'國內生產總值'},
                {'key': 'years', 'value': '[2015, 2016]'},
                {'key': 'last_year', 'value': 2016},
                {'key': 'location', 'value': '{"country": "China"}'},
            ]
        }
        assert out.get('extras') == exp.get('extras')

    def test_name_is_used_if_theres_no_title(self):
        indict = {'name': 'gdp'}
        out = converter.resource(indict)
        assert out.get('name') == indict['name']

    def test_resource_title_is_used_as_name(self):
        indict = {
            'name': 'gdp',
            'title': 'Gross domestic product',
        }

        out = converter.resource(indict)
        assert out.get('name') == indict['title']

    def test_path_to_url(self):
        # Test remote path
        indict = {'path': 'http://www.somewhere.com/data.csv'}
        out = converter.resource(indict)
        assert out['url'] == indict['path']

        # Test local path
        indict = {'path': './data.csv'}
        out = converter.resource(indict)
        assert out['url'] == indict['path']

        # Test POSIX path
        indict = {'path': '/home/user/data.csv'}
        out = converter.resource(indict)
        assert out['url'] == indict['path']

    def test_passthrough(self):
        indict = {
            'description': 'GDPs list',
            'format': 'CSV',
            'hash': 'e785c0883d7a104330e69aee73d4f235'
        }
        out = converter.resource(indict)
        assert out == indict

    def test_schema(self):
        schema = {
            'fields': [
                {'name': 'id', 'type': 'integer'},
                {'name': 'title', 'type': 'string'},
            ]
        }
        indict = {
            'schema': schema
        }
        out = converter.resource(indict)
        assert out['schema'] == indict['schema']


class TestPackageConversion:
    def test_passthrough(self):
        indict = {
            'name': 'gdp',
            'title': 'Countries GDP',
            'version': '1.0',
        }
        out = converter.package(indict)
        assert out['name'] == indict['name']
        assert out['title'] == indict['title']
        assert out['version'] == indict['version']

    def test_description_is_converted_to_notes(self):
        indict = {
            'description': 'Country, regional and world GDP in current USD.'
        }
        out = converter.package(indict)
        assert out.get('notes') == indict['description']

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

    def test_sources(self):
        indict = {
            'sources': [
                {
                    'title': 'World Bank and OECD'
                }
            ]
        }
        out = converter.package(indict)
        assert out.get('author') == indict['sources'][0]['title']
        indict = {
            'sources': [
                {
                    'email': 'data@worldbank.org',
                    'path': 'http://data.worldbank.org/indicator/NY.GDP.MKTP.CD',
                    'title': 'World Bank and OECD'
                }
            ]
        }
        out = converter.package(indict)
        assert out.get('author') == indict['sources'][0]['title']
        assert out.get('author_email') == indict['sources'][0]['email']
        assert out.get('url') == indict['sources'][0]['path']

        # Make sure that multiple sources are stored in "extras".
        # Ensure that the properties `author`, `author_email` and `url` are
        # still set to the data found in the first source.
        indict = {
            'sources': [
                {
                    'email': 'data@worldbank.org',
                    'path': 'http://data.worldbank.org/indicator/NY.GDP.MKTP.CD',
                    'title': 'World Bank and OECD'
                },
                {
                    'email': 'data2@worldbank2.org',
                    'path': 'http://data2.worldbank2.org/indicator/NY.GDP.MKTP.CD',
                    'title': 'World Bank 2 and OECD'
                }
            ]
        }
        out = converter.package(indict)
        exp = {
            'extras': [{
                'sources': indict['sources']
            }],
            'author': 'World Bank and OECD',
            'author_email': 'data@worldbank.org',
            'url': 'http://data.worldbank.org/indicator/NY.GDP.MKTP.CD'
        }
        assert out == exp

    # TODO: get clear on the spelling of the key "organization".
    # It's "organisation" in the JSON schema at
    # https://specs.frictionlessdata.io/schemas/data-package.json
    # while it's "organization" in the page of the specs at
    # https://specs.frictionlessdata.io/data-package/#metadata
    def test_contributors(self):
        author_name = 'John Smith'
        author_email = 'jsmith@email.com'
        author_name2 = 'Johnny Smith'
        author_email2 = 'jsmith2@email.com'
        org_name = 'My Organization'
        indict = {
            'contributors': [
                {'title': author_name}
            ]
        }
        out = converter.package(indict)
        assert out.get('maintainer') == author_name

        # Make sure we store in "extras" if some keys don't have equivalent
        # mappings in CKAN
        indict = {
            'contributors': [
                {
                    'title': author_name,
                    'email': author_email,
                    'path': 'file.csv',
                    'organisation': org_name,
                    'role': 'maintainer',
                }
            ]
        }
        exp = {
            'extras': [{
                'contributors': indict['contributors']
            }],
            'maintainer': author_name,
            'maintainer_email': author_email
        }
        out = converter.package(indict)
        assert out == exp

        # Make sure that we also get the correct data when there are multiple
        # contributors
        indict = {
            'contributors': [
                {
                    'title': author_name2,
                    'email': author_email2,
                },
                {
                    'title': author_name,
                    'email': author_email,
                    'path': 'file.csv'
                }
            ]
        }
        exp = {
            'extras': [{
                'contributors': indict['contributors']
            }],
            'maintainer': author_name2,
            'maintainer_email': author_email2
        }
        out = converter.package(indict)
        assert out == exp

    def test_keywords_converted_to_tags(self):
        keywords = ['economy!!!', 'World Bank']
        indict = {'keywords': keywords}
        out = converter.package(indict)
        assert out.get('tags') == [
            {'name': 'economy'},
            {'name': 'world-bank'},
        ]

    def test_extras_is_converted(self):
        indict = {
            'homepage': 'www.example.com',
            'newdict': {'key1': 'dict_to_jsonify'},
            'newint': 123,
            'newkey': 'new value',
            'newlist': [1, 2, 3, 'string'],
            'title': 'Title here'
        }
        exp = {
            'title': 'Title here',
            'url': 'www.example.com',
            'extras': [
                {
                    'key': 'newdict', 'value': '{"key1": "dict_to_jsonify"}'
                },
                {'key': 'newint', 'value': 123},
                {'key': 'newkey', 'value': 'new value'},
                {'key': 'newlist', 'value': '[1, 2, 3, "string"]'},
            ]
        }
        out = converter.package(indict)
        assert out == exp
