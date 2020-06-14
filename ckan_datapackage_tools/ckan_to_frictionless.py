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

    def resource(self, ckandict):
        outdict = dict(ckandict)
        for k, v in self.resource_mapping.items():
            if k in outdict:
                outdict[v] = outdict[k]
                del outdict[k]
        return outdict

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
            # Remove keys not needed
            del res['package_id']
            del res['position']

            # Reformat expected output for some keys in resource
            res['format'] = res['format'].lower()
            res['name'] = res['name'].lower().replace(' ', '-')

            # Remap differences from CKAN to Frictionless resource
            for k, v in self.resource_mapping.items():
                if k in res:
                    res[v] = res[k]
                    del res[k]

                    # Cast CKAN resource size to int
                    if k == 'size':
                        if not res[v]:  # receives `null`
                            res[v] = 0
                        else:
                            res[v] = int(res[v])

        return outdict
