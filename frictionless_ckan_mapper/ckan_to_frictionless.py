'''
Convert CKAN packages and resources to their
Frictionless equivalent.
'''
# Standard library imports
import json

# Third-party library imports
import slugify

try:
    json_parse_exception = json.decoder.JSONDecodeError
except AttributeError:  # Testing against Python 2
    json_parse_exception = ValueError


class CKANToFrictionless:
    '''Set of methods to convert CKAN packages and resources to their
    Frictionless equivalent.'''

    @staticmethod
    def _resource_keys_to_remove(resource):
        # TODO: Do we want to keep everything except `package_id` and
        # `position`? The current test
        # `test_resource_path_is_set_even_for_uploaded_resources`
        # is not expecting `url_type` in its output.
        resource_keys_to_remove = ['package_id', 'position', 'url_type']

        # TODO: delete keys last as may be needed for something in processing
        for k in resource_keys_to_remove:
            if k in resource:
                del resource[k]
        return resource

    @staticmethod
    def _remap_resource_ckan_to_frictionless(resource):
        '''Remap differences from CKAN to Frictionless resource'''
        resource_mapping = {
            'size': 'bytes',
            'mimetype': 'mediatype',
            'url': 'path'
        }

        for key, value in resource_mapping.items():
            if key in resource:
                resource[value] = resource[key]
                del resource[key]

                # Cast CKAN resource size to int
                if key == 'size':
                    if not resource[value]:  # receives `null`
                        resource[value] = 0
                    else:
                        resource[value] = int(resource[value])
        return resource

    def resource(self, ckandict):
        '''Convert a CKAN resource to Frictionless Resource.

        1. Remove unneeded keys
        2. Expand extras.
            * Extras are already expanded to key / values by CKAN (unlike on
            * package) ~~Apply heuristic to unjsonify (if starts with [ or {
            * unjsonify~~ JSON loads everything and on error have a string
        3. Map keys from CKAN to Frictionless (and reformat if needed)
        4. Remove keys with null values (CKAN has a lot of null valued keys)
        4. Apply special formatting for key fields
        '''
        resource = dict(ckandict)
        resource = self._resource_keys_to_remove(resource)

        # TODO: remove as CKAN Resource does not have extras (CKAN has already
        # unpacked them)
        if 'extras' in resource:
            resource['extras'] = json.loads(resource['extras'])

        # Unjsonify values
        # slightly hacky way to check if value is a jsonified array or dict
        for key, value in resource.items():
            if isinstance(value, str):
                value = value.strip()
                if value.startswith('{') or value.startswith('['):
                    try:
                        value = json.loads(value)
                        resource[key] = value
                    except (json_parse_exception, TypeError):
                        pass

        # Reformat expected output for some keys in resource
        # resource['format'] = resource['format'].lower()
        if 'name' in resource:
            resource['name'] = slugify.slugify(resource['name']).lower()

        resource = self._remap_resource_ckan_to_frictionless(resource)
        return resource

    @staticmethod
    def _remap_package_keys(ckandict, outdict):
        '''Remap necessary package keys.'''
        package_mapping = {
            'notes': 'description',
            'tags': 'keywords',  # this is flattened and simplified
        }
        for key, value in package_mapping.items():
            if key in ckandict and key == 'url':
                outdict[value] = ckandict[key]
                del outdict[key]
            elif key in ckandict and key == 'tags':
                outdict[value] = []
                for tag in ckandict[key]:
                    outdict[value].append(tag['name'])
                del outdict[key]
            elif key in ckandict:
                outdict[value] = ckandict[key]
                del outdict[key]
        return outdict

    @staticmethod
    def _convert_package_extras(outdict):
        '''Convert the structure of extras.'''
        if outdict.get('extras'):
            extras = outdict['extras']  # this is a list
            outdict['extras'] = {}  # we convert to dict
            for extra in extras:
                key = extra['key']
                value = extra['value']
                try:
                    value = json.loads(value)
                except (json_parse_exception, TypeError):
                    pass
                result = {key: value}
                outdict['extras'].update(result)
        return outdict

    @staticmethod
    def _remap_package_sources(outdict):
        '''Remap properties in sources.'''
        package_sources_mapping = {
            'author': 'title',
            'author_email': 'email',
            'url': 'path',
        }
        outdict['sources'] = []
        source = {}
        for key, value in package_sources_mapping.items():
            if key in outdict:
                source[value] = outdict[key]
                del outdict[key]
        outdict['sources'].append(source)
        return outdict

    def dataset(self, ckandict):
        '''Convert a CKAN Package (Dataset) to Frictionless Package.

        1. Remove unneeded keys
        2. Expand extras.
            * ~~Apply heuristic to unjsonify (if starts with [ or { unjsonify~~
            * JSON loads everything and on error have a string
        3. Map keys from CKAN to Frictionless (and reformat if needed)
        4. Remove keys with null values (CKAN has a lot of null valued keys)
        4. Apply special formatting for key fields
        '''
        outdict = dict(ckandict)
        outdict = self._remap_package_keys(ckandict, outdict)
        outdict = self._convert_package_extras(outdict)
        outdict = self._remap_package_sources(outdict)

        # Reformat expected output for some keys in package
        outdict['name'] = outdict['name'].replace('-', '_')

        # Reformat resources inside package
        outdict['resources'] = [
            self.resource(res) for res in outdict['resources']
        ]

        return outdict
