import json

try:
    json_parse_exception = json.decoder.JSONDecodeError
except AttributeError:  # Testing against Python 2
    json_parse_exception = ValueError


resource_mapping = {
    'bytes': 'size',
    'mediatype': 'mimetype',
    'path': 'url'
}

package_mapping = {
    'description': 'notes',
    'homepage': 'url',
}

# Any key not in this list is passed as is inside "extras".
# Further processing will happen for possible matchings, e.g.
# contributor <=> author
ckan_package_keys = [
    'author',
    'author_email',
    'groups',
    'license_id',
    'license_title',
    'maintainer',
    'maintainer_email',
    'name',
    'notes',
    'owner_org',
    'private',
    'relationships_as_object',
    'relationships_as_subject',
    'resources',
    'state',
    'tags',
    'title',
    'type',
    'url',
    'version'
]

frictionless_package_keys_to_exclude = [
    'extras',
    'keywords'
]


def resource(fddict):
    '''Convert a Frictionless resource to a CKAN resource.

    # TODO: (the following is inaccurate)

    1. Map keys from Frictionless to CKAN (and reformat if needed).
    2. Apply special formatting (if any) for key fields e.g. slugify.
    '''
    resource = dict(fddict)

    # Remap differences from Frictionless to CKAN resource
    for key, value in resource_mapping.items():
        if key in resource:
            resource[value] = resource[key]
            del resource[key]

    return resource


def package(fddict):
    '''Convert a Frictionless package to a CKAN package (dataset).

    # TODO: (the following is inaccurate)

    1. Map keys from Frictionless to CKAN (and reformat if needed).
    2. Apply special formatting (if any) for key fields.
    3. Copy extras across inside the "extras" key.
    '''
    outdict = dict(fddict)

    # Map data package keys
    for key, value in package_mapping.items():
        if key in fddict:
            outdict[value] = fddict[key]
            del outdict[key]

    if 'licenses' in outdict and outdict['licenses']:
        outdict['license_id'] = outdict['licenses'][0].get('name')
        outdict['license_title'] = outdict['licenses'][0].get('title')

    if outdict.get('contributors'):
        for c in outdict['contributors']:
            if c.get('role') in [None, 'author']:
                outdict['author'] = c.get('title')
                outdict['author_email'] = c.get('email')
                break

        for c in outdict['contributors']:
            if c.get('role') == 'maintainer':
                outdict['maintainer'] = c.get('title')
                outdict['maintainer_email'] = c.get('email')
                break

    if outdict.get('keywords'):
        outdict['tags'] = [
            {'name': keyword} for keyword in outdict['keywords']
        ]
        del outdict['keywords']

    final_dict = dict(outdict)
    for key, value in outdict.items():
        if (
            key not in ckan_package_keys and
            key not in frictionless_package_keys_to_exclude
        ):
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            if not final_dict.get('extras'):
                final_dict['extras'] = []
            final_dict['extras'].append(
                {'key': key, 'value': value}
            )
            del final_dict[key]
    outdict = dict(final_dict)

    return outdict
