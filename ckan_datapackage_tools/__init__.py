class CKANToFrictionless(object):

    resource_mapping = {
      'size': 'bytes',
      'mimetype': 'mediatype',
      'url': 'path'
    }

    def resource(self, ckandict):
        outdict = dict(ckandict)
        for k,v in self.resource_mapping.items():
            if k in outdict:
                outdict[v] = outdict[k]
                del outdict[k]
        return outdict