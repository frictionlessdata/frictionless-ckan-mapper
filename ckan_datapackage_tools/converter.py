'''Functions for converting between CKAN's dataset and Data Packages.
'''
import re
import json

import six
import slugify


def _convert_to_datapackage_resource(resource_dict):
    '''Convert a CKAN resource dict into a Data Package resource dict.

    '''
    resource = {}

    if resource_dict.get('url'):
        resource['path'] = resource_dict['url']
    # TODO: DataStore only resources?

    if resource_dict.get('description'):
        resource['description'] = resource_dict['description']

    if resource_dict.get('format'):
        resource['format'] = resource_dict['format']

    if resource_dict.get('hash'):
        resource['hash'] = resource_dict['hash']

    if resource_dict.get('name'):
        resource['name'] = slugify.slugify(resource_dict['name']).lower()
        resource['title'] = resource_dict['name']
    else:
        resource['name'] = resource_dict['id']

    schema = resource_dict.get('schema')
    if isinstance(schema, six.string_types):
        try:
            resource['schema'] = json.loads(schema)
        except ValueError:
            # Assume it's a path or URL
            resource['schema'] = schema
    elif isinstance(schema, dict):
        resource['schema'] = schema

    return resource


def dataset_to_datapackage(dataset_dict):
    '''Convert the given CKAN dataset dict into a Data Package dict.

    :returns: the datapackage dict
    :rtype: dict

    '''
    PARSERS = [
        _rename_dict_key('title', 'title'),
        _rename_dict_key('version', 'version'),
        _parse_ckan_url,
        _parse_notes,
        _parse_tags,
        _parse_extras,
    ]
    dp = {
        'name': dataset_dict['name']
    }

    for parser in PARSERS:
        dp.update(parser(dataset_dict))

    resources = dataset_dict.get('resources')
    if resources:
        dp['resources'] = [_convert_to_datapackage_resource(r)
                           for r in resources]

    # Ensure unique resource names
    names = {}
    for resource in dp.get('resources', []):
        if resource['name'] in names.keys():
            resource['name'] = resource['name'] + str(names[resource['name']])
            names[resource['name']] += 1
        else:
            names[resource['name']] = 0

    return dp


def datapackage_to_dataset(datapackage):
    '''Convert the given datapackage into a CKAN dataset dict.

    :returns: the dataset dict
    :rtype: dict
    '''
    PARSERS = [
        _rename_dict_key('title', 'title'),
        _rename_dict_key('version', 'version'),
        _rename_dict_key('description', 'notes'),
        _datapackage_parse_license,
        _datapackage_parse_sources,
        _datapackage_parse_author,
        _datapackage_parse_keywords,
        _datapackage_parse_unknown_fields_as_extras,
    ]
    dataset_dict = {
        'name': datapackage.descriptor['name'].lower()
    }

    for parser in PARSERS:
        dataset_dict.update(parser(datapackage.descriptor))

    if datapackage.resources:
        dataset_dict['resources'] = [_datapackage_resource_to_ckan_resource(r)
                                     for r in datapackage.resources]

    return dataset_dict


def _datapackage_resource_to_ckan_resource(resource):
    resource_dict = {}

    if resource.descriptor.get('name'):
        name = resource.descriptor.get('title') or resource.descriptor['name']
        resource_dict['name'] = name

    if resource.local:
        resource_dict['path'] = resource.source
    elif resource.remote:
        resource_dict['url'] = resource.source
    elif resource.inline:
        resource_dict['data'] = resource.source
    else:
        raise NotImplemented('Multipart resources not yet supported')

    if resource.descriptor.get('description'):
        resource_dict['description'] = resource.descriptor['description']

    if resource.descriptor.get('format'):
        resource_dict['format'] = resource.descriptor['format']

    if resource.descriptor.get('hash'):
        resource_dict['hash'] = resource.descriptor['hash']

    if resource.descriptor.get('schema'):
        resource_dict['schema'] = resource.descriptor['schema']

    return resource_dict


def _rename_dict_key(original_key, destination_key):
    def _parser(the_dict):
        result = {}

        if the_dict.get(original_key):
            result[destination_key] = the_dict[original_key]

        return result
    return _parser


def _parse_ckan_url(dataset_dict):
    result = {}

    if dataset_dict.get('ckan_url'):
        result['homepage'] = dataset_dict['ckan_url']

    return result


def _parse_notes(dataset_dict):
    result = {}

    if dataset_dict.get('notes'):
        result['description'] = dataset_dict['notes']

    return result


def _parse_tags(dataset_dict):
    result = {}

    keywords = [tag['name'] for tag in dataset_dict.get('tags', [])]

    if keywords:
        result['keywords'] = keywords

    return result


def _parse_extras(dataset_dict):
    result = {}
    extras = [[extra['key'], extra['value']] for extra
              in dataset_dict.get('extras', [])]
    for extra in extras:
        try:
            extra[1] = json.loads(extra[1])
        except (ValueError, TypeError):
            pass
    sources = _parse_organization_as_primary_source(dataset_dict)
    licenses = _parse_primary_license(dataset_dict)
    contributors = _parse_primary_contributors(dataset_dict)
    if extras:
        extras_dict = dict(extras)
        result.update(_parse_profile(extras_dict))
        _parse_extra_sources(extras_dict, sources)
        _parse_extra_licenses(extras_dict, licenses)
        _parse_extra_contributors(extras_dict, contributors)
        if extras_dict:
            result['extras'] = extras_dict
    if sources:
        result['sources'] = sources
    if licenses:
        result['licenses'] = licenses
    if contributors:
        result['contributors'] = contributors
    return result


def _parse_profile(dataset_dict):
    result = {}
    profile = dataset_dict.pop('profile', '')
    if profile:
        result['profile'] = profile
    return result


def _parse_organization_as_primary_source(dataset_dict):
    all_sources = []
    source = {}
    organization = dataset_dict.get('organization')
    if organization.get('is_organization', False):
        source['title'] = organization.get('name', organization.get('title'))
    if source.get('title'):
        if dataset_dict.get('url'):
            source['path'] = dataset_dict['url']
        all_sources.append(source)
    return all_sources


def _parse_extra_sources(extras_dict, sources):
    for source in extras_dict.pop('sources', []):
        parsed = _parse_source(source)
        if parsed:
            source.update(parsed)
        sources.append(source)


def _parse_source(dataset_dict):
    source = {}
    # ckan values trump frictionless values
    if dataset_dict.get('url'):
        source['path'] = dataset_dict['url']
    return source


def _parse_primary_license(dataset_dict):
    licenses = []
    license = _parse_license(dataset_dict)
    if license:
        licenses.append(license)
    return licenses


def _parse_extra_licenses(extras_dict, licenses):
    for license in extras_dict.pop('licenses', []):
        parsed = _parse_license(license)
        # include existing valid license properties
        if parsed:
            license.update(parsed)
        licenses.append(license)


def _parse_license(dataset_dict):
    license = {}
    # ckan values trump frictionless values
    if dataset_dict.get('license_id'):
        license['name'] = dataset_dict['license_id']
    if dataset_dict.get('license_title'):
        license['title'] = dataset_dict['license_title']
    if dataset_dict.get('license_url'):
        license['path'] = dataset_dict['license_url']
    return license


def _parse_primary_contributors(dataset_dict):
    contributors = []
    for parser in [_parse_author_as_contributor,
                   _parse_maintainer_as_contributor]:
        parsed = parser(dataset_dict)
        if parsed:
            contributors.append(parsed)
    return contributors


def _parse_author_as_contributor(dataset_dict):
    contributor = {}
    if dataset_dict.get('author'):
        contributor['title'] = dataset_dict['author']
        contributor['role'] = 'author'
    if dataset_dict.get('author_email'):
        contributor['email'] = dataset_dict['author_email']
    return contributor


def _parse_maintainer_as_contributor(dataset_dict):
    contributor = {}
    if dataset_dict.get('maintainer'):
        contributor['title'] = dataset_dict['maintainer']
        contributor['role'] = 'maintainer'
    if dataset_dict.get('maintainer_email'):
        contributor['email'] = dataset_dict['maintainer_email']
    return contributor


def _parse_extra_contributors(extras, contributors):
    for contributor in extras.pop('contributors', []):
        parsed = _parse_contributor(contributor)
        if parsed:
            contributors.append(parsed)


def _parse_contributor(contributor):
    if contributor.get('title'):
        if not contributor.get('role'):
            contributor['role'] = 'contributor'
    else:
        contributor = {}
    return contributor


def _datapackage_parse_license(datapackage_dict):
    result = {}

    license = datapackage_dict.get('license')
    if license:
        if isinstance(license, dict):
            if license.get('type'):
                result['license_id'] = license['type']
            if license.get('title'):
                result['license_title'] = license['title']
            if license.get('title'):
                result['license_url'] = license['url']
        elif isinstance(license, six.string_types):
            result['license_id'] = license

    return result


def _datapackage_parse_sources(datapackage_dict):
    result = {}

    sources = datapackage_dict.get('sources')
    if sources:
        author = sources[0].get('name')
        author_email = sources[0].get('email')
        source = sources[0].get('web')
        if author:
            result['author'] = author
        if author_email:
            result['author_email'] = author_email
        if source:
            result['url'] = source

    return result


def _datapackage_parse_author(datapackage_dict):
    result = {}

    author = datapackage_dict.get('author')
    if author:
        maintainer = maintainer_email = None

        if isinstance(author, dict):
            maintainer = author.get('name')
            maintainer_email = author.get('email')
        elif isinstance(author, six.string_types):
            match = re.match(r'(?P<name>[^<]+)'
                             r'(?:<(?P<email>\S+)>)?',
                             author)

            maintainer = match.group('name')
            maintainer_email = match.group('email')

        if maintainer:
            result['maintainer'] = maintainer.strip()
        if maintainer_email:
            result['maintainer_email'] = maintainer_email

    return result


def _datapackage_parse_keywords(datapackage_dict):
    result = {}

    keywords = datapackage_dict.get('keywords')
    if keywords:
        result['tags'] = [{'name': slugify.slugify(keyword)}
                          for keyword in keywords]

    return result


def _datapackage_parse_unknown_fields_as_extras(datapackage_dict):
    # FIXME: It's bad to hardcode it here. Instead, we should change the
    # parsers pattern to remove whatever they use from the `datapackage_dict`
    # and call this parser at last. Anything that's still in `datapackage_dict`
    # would then be added to extras.
    KNOWN_FIELDS = [
        'name',
        'resources',
        'license',
        'title',
        'description',
        'homepage',
        'version',
        'sources',
        'author',
        'keywords',
    ]

    result = {}
    extras = [{'key': k, 'value': v}
              for k, v in datapackage_dict.items()
              if k not in KNOWN_FIELDS]

    if extras:
        for extra in extras:
            value = extra['value']
            if isinstance(value, dict) or isinstance(value, list):
                extra['value'] = json.dumps(value)
        result['extras'] = extras

    return result
