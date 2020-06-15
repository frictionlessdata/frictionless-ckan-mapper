import json

import slugify


class CKANToFrictionless:

    resource_mapping = {
        'size': 'bytes',
        'mimetype': 'mediatype',
        'url': 'path'
    }

    # TODO: Do we want to keep everything except `package_id` and
    # `position`? The current test
    # `test_resource_path_is_set_even_for_uploaded_resources`
    # is not expecting `url_type` in its output.
    resource_keys_to_remove = ['package_id', 'position', 'url_type']

    def ckan_resource_to_fd_resource(self, ckandict):
        '''Convert a CKAN resource to Frictionless Resource.

        1. Remove unneeded keys
        2. Expand extras.
            * Extras are already expanded to key / values by CKAN (unlike on package)
            * ~~Apply heuristic to unjsonify (if starts with [ or { unjsonify~~
            * JSON loads everything and on error have a string
        3. Map keys from CKAN to Frictionless (and reformat if needed)
        4. Remove keys with null values (CKAN has a lot of null valued keys)
        4. Apply special formatting for key fields
        '''
        resource = dict(ckandict)
        for k in self.resource_keys_to_remove:
            if k in resource:
                del resource[k]

        if 'extras' in resource:
            resource['extras'] = json.loads(resource['extras'])

        if 'schema' in resource:
            try:
                resource['schema'] = json.loads(resource['schema'])
            except (json.decoder.JSONDecodeError, TypeError):
                pass

        # Reformat expected output for some keys in resource
        # resource['format'] = resource['format'].lower()
        if 'name' in resource:
            resource['title'] = resource['name']
            resource['name'] = slugify.slugify(resource['name']).lower()

        # Remap differences from CKAN to Frictionless resource
        for k, v in self.resource_mapping.items():
            if k in resource:
                resource[v] = resource[k]
                del resource[k]

                # Cast CKAN resource size to int
                if k == 'size':
                    if not resource[v]:  # receives `null`
                        resource[v] = 0
                    else:
                        resource[v] = int(resource[v])
        return resource

    package_mapping = {
        'notes': 'description',
        'tags': 'keywords',  # this is flattened and simplified
    }

    package_sources_mapping = {
        'author': 'title',
        'author_email': 'email',
        'url': 'path',
    }

    def dataset_to_datapackage(self, ckandict):
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

        # Remap necessary package keys
        for k, v in self.package_mapping.items():
            if k in ckandict and k == 'url':
                outdict[v] = ckandict[k]
                del outdict[k]
            elif k in ckandict and k == 'tags':
                outdict[v] = []
                for tag in ckandict[k]:
                    outdict[v].append(tag['name'])
                del outdict[k]
            elif k in ckandict:
                outdict[v] = ckandict[k]
                del outdict[k]

        # Convert the structure of extras
        if outdict.get('extras'):
            extras = outdict['extras']  # this is a list
            outdict['extras'] = {}  # we convert to dict
            for extra in extras:
                key = extra['key']
                value = extra['value']
                try:
                    value = json.loads(value)
                except (json.decoder.JSONDecodeError, TypeError):
                    pass
                result = {key: value}
                outdict['extras'].update(result)

        # Remap properties in sources
        outdict['sources'] = []
        source = {}
        for k, v in self.package_sources_mapping.items():
            if k in outdict:
                source[v] = outdict[k]
                del outdict[k]
        outdict['sources'].append(source)

        # Reformat expected output for some keys in package
        outdict['name'] = outdict['name'].replace('-', '_')

        # Reformat resources inside package
        outdict['resources'] = [self.ckan_resource_to_fd_resource(
            res) for res in outdict['resources']]

        return outdict
