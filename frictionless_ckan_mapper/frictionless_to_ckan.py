import json

try:
    json_parse_exception = json.decoder.JSONDecodeError
except AttributeError:  # Testing against Python 2
    json_parse_exception = ValueError


class FrictionlessToCKAN:

    # TODO: How do we map the required CKAN `package_id`?
    # TODO: In CKAN, `private` is another required field:
    #       set default value to False?

    resource_mapping = {
        'bytes': 'size',
        'mediatype': 'mimetype',
        'path': 'url'
    }

    # TODO: Do we passthrough all the FD properties not found in CKAN?
    # `data`: This replaces Resource.path if it is not specified.
    #         However, it is not an URL. Should it just passthrough?
    # `homepage`: Does this passthrough? What if we also have FD Resource.path
    #             => we can't map both to CKAN Resource.url
    # `licenses`: How do we map multiple licenses from Frictionless to CKAN?
    resource_keys_to_remove = [
        '',
    ]

    def resource(self, fddict):
        '''Convert a Frictionless resource to a CKAN resource.

        # TODO: (the following is inaccurate)

        1. Remove unneeded keys (are there any keys to remove?)
        2. Convert extras: "dict" to "list of dict".
        3. Map keys from Frictionless to CKAN (and reformat if needed).
        4. Remove keys with null values.
        5. Apply special formatting (if any) for key fields e.g. slugify
        '''
        pass

    def package(self, fddict):
        '''Convert a Frictionless package to a CKAN package (dataset).

        # TODO: (the following is inaccurate)

        1. Copy extras across.  # Is this true?
        2. Map keys from Frictionless to CKAN (and reformat if needed).
        3. Remove keys with null values (CKAN has a lot of null valued keys).
        4. Remove unneeded keys.
        5. Apply special formatting for key fields.
        '''
        pass
