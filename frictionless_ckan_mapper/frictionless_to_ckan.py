# coding=utf-8
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
    'creator_user_id',
    'groups',
    'id',
    'license_id',
    'license_title',
    'license_url',
    'maintainer',
    'maintainer_email',
    'metadata_created',
    'metadata_modified',
    'name',
    'notes',
    'owner_org',
    'private',
    'relationships_as_object',
    'relationships_as_subject',
    'revision_id',
    'resources',
    'state',
    'tags',
    'tracking_summary',
    'title',
    'type',
    'url',
    'version'
]

frictionless_package_keys_to_exclude = [
    'extras'
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

    # map resources inside dataset
    if 'resources' in fddict:
        outdict['resources'] = [resource(res) for res in fddict['resources']]

    if 'licenses' in outdict and outdict['licenses']:
        outdict['license_id'] = outdict['licenses'][0].get('name')
        outdict['license_title'] = outdict['licenses'][0].get('title')
        outdict['license_url'] = outdict['licenses'][0].get('path')
        # remove it so it won't get put in extras
        if len(outdict['licenses']) == 1:
            outdict.pop('licenses', None)

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

        # we remove contributors where we have extracted everything into
        # ckan core that way it won't end up in extras
        # this helps ensure that round tripping with ckan is good
        # when have we extracted everything?
        # if contributors has length 1 and role in author or maintainer
        # or contributors == 2 and no of authors and maintainer types <= 1
        if (
            (len(outdict.get('contributors')) == 1 and
                outdict['contributors'][0].get('role') in [None, 'author',
                    'maintainer'])
            or
            (len(outdict.get('contributors')) == 2 and
                [c.get('role') for c in outdict['contributors']]
                not in (
                    [None, None],
                    ['maintainer', 'maintainer'],
                    ['author', 'author']))
                    ):
            outdict.pop('contributors', None)

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
