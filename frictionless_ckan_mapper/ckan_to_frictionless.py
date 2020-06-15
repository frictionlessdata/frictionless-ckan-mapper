class CKANToFrictionless:

    resource_mapping = {
        'size': 'bytes',
        'mimetype': 'mediatype',
        'url': 'path'
    }

    resource_keys_to_remove = [ 'package_id', 'position' ]

    def resource(self, ckandict):
        '''Convert a CKAN resource to Frictionless Resource.
        
        1. Remove unneeded keys
        2. Expand extras.
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

        # Reformat expected output for some keys in resource
        resource['format'] = resource['format'].lower()
        resource['name'] = resource['name'].lower().replace(' ', '-')

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
        'tags': 'keywords',  # this is flattened and simplified
        'url': 'homepage'
    }

    def package(self, ckandict):
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

        # Remap keys `url` and `tags` to Frictionless
        # format `path` and `keywords`
        for k, v in self.package_mapping.items():
            if k in ckandict and k == 'url':
                outdict[v] = ckandict[k]
                del outdict[k]
            if k in ckandict and k == 'tags':
                outdict[v] = []
                for tag in ckandict[k]:
                    outdict[v].append(tag['name'])
                del outdict[k]

        # Reformat expected output for some keys in package
        outdict['title'] = outdict['title'].replace(' ', '-')
        outdict['name'] = outdict['name'].replace('-', '_')

        # Reformat resources inside package
        outdict['resources'] = [ self.resource(res) for res in outdict['resources'] ]

        return outdict
