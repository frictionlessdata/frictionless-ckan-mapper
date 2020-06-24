import json

try:
    json_parse_exception = json.decoder.JSONDecodeError
except AttributeError:  # Testing against Python 2
    json_parse_exception = ValueError


class FrictionlessToCKAN:

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
        "author",
        "author_email",
        "groups",
        "license_id",
        "maintainer",
        "maintainer_email",
        "name",
        "notes",
        "owner_org",
        "private",
        "relationships_as_object",
        "relationships_as_subject",
        "resources",
        "state",
        "tags",
        "title",
        "type",
        "url",
        "version"
    ]

    def resource(self, fddict):
        '''Convert a Frictionless resource to a CKAN resource.

        # TODO: (the following is inaccurate)

        1. Convert extras: "dict" to "list of dict".
        2. Map keys from Frictionless to CKAN (and reformat if needed).
        3. Apply special formatting (if any) for key fields e.g. slugify.
        4. Map anything not in CKAN inside the "extras" key.
        '''
        pass

    def package(self, fddict):
        '''Convert a Frictionless package to a CKAN package (dataset).

        # TODO: (the following is inaccurate)

        1. Map keys from Frictionless to CKAN (and reformat if needed).
        2. Apply special formatting (if any) for key fields.
        3. Copy extras across inside the "extras" key.
        '''
        outdict = dict(fddict)

        # Map data package keys
        for k, v in self.package_mapping.items():
            if k in fddict:
                outdict[v] = fddict[k]
                del outdict[k]

        if outdict.get('licenses'):
            outdict['license_id'] = outdict['licenses'][0]['type']
            if outdict['licenses'][0].get('title'):
                outdict['license_title'] = outdict['licenses'][0]['title']
            if len(outdict.get('licenses')) > 1:
                if not outdict.get('extras'):
                    outdict['extras'] = []
                outdict['extras'].append({'licenses': outdict['licenses']})
            del outdict['licenses']

        return outdict
