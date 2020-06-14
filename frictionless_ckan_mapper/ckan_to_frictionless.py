class CKANToFrictionless:

    resource_mapping = {
        'size': 'bytes',
        'mimetype': 'mediatype',
        'url': 'path'
    }

    package_mapping = {
        'tags': 'keywords',  # this is flattened and simplified
        'url': 'homepage'
    }

    def _convert_resource_format(self, resource):
        '''Remove unneeded keys, cast to expected type and reformat
        keys by removing capitalization and converting symbols.'''
        # Remove keys not needed
        del resource['package_id']
        del resource['position']

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

    def resource(self, ckandict):
        return self._convert_resource_format(ckandict)

    def package(self, ckandict):
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
        for res in outdict['resources']:
            res = self._convert_resource_format(res)

        return outdict
