import json

import frictionless_ckan_mapper.ckan_to_frictionless as ckan_to_frictionless
import frictionless_ckan_mapper.frictionless_to_ckan as frictionless_to_ckan

import six


class TestPackageConversion:
    def test_round_trip_ckan(self):
        # `ckan1` != `ckan2` but `ckan2` == `ckan3`
        inpath = 'tests/fixtures/full_ckan_package.json'
        ckan1 = json.load(open(inpath))
        fd1 = ckan_to_frictionless.dataset(ckan1)
        ckan2 = frictionless_to_ckan.package(fd1)
        fd2 = ckan_to_frictionless.dataset(ckan2)
        ckan3 = frictionless_to_ckan.package(fd2)

        # FIXME: this currently doesn't work for Python 2 due to the way
        # Unicode is handled and because the dictionary keys do not keep
        # the same order.
        # Solution 1: Skip for Python 2 (it's clearly the same dictionary
        # if the build passes on Python 3)
        # Solution 2: Hard code the dicts as in `test_extras_is_converted`
        # in test_frictionless_to_ckan.py instead of loading JSON and
        # sort the keys.
        if not six.PY2:
            assert ckan2 == ckan3

    def test_differences_ckan_round_trip(self):
        # When converting ckan1 to fd1 then fd1 to ckan2,
        # ckan1 is bound to differ from ckan2.
        # Those fixtures illustrate the expected differences.
        inpath = 'tests/fixtures/full_ckan_package.json'
        ckan1 = json.load(open(inpath))
        fd1 = ckan_to_frictionless.dataset(ckan1)
        ckan2 = frictionless_to_ckan.package(fd1)
        inpath_round_trip = ('tests/fixtures/'
                             'full_ckan_package_first_round_trip.json')
        exp = json.load(open(inpath_round_trip))

        # FIXME: this currently doesn't work for Python 2 due to the way
        # Unicode is handled and because the dictionary keys do not keep
        # the same order.
        # Solution 1: Skip for Python 2 (it's clearly the same dictionary
        # if the build passes on Python 3)
        # Solution 2: Hard code the dicts as in `test_extras_is_converted`
        # in test_frictionless_to_ckan.py instead of loading JSON and
        # sort the keys.
        if not six.PY2:
            assert ckan2 == exp

        # Notable differences in `exp` from ckan1 are:
        # - Keys not defined in a standard CKAN package such as
        #  `creator_user_id` will go to `extras`.
        # - In our `full_ckan_package.json` fixture, 'extras' is empty but
        #   Frictionless fills it and it will exist in the CKAN package after
        #   the first round trip.
        # - Keys defined in CKAN but ignored in Frictionless, such as `id`
        #   (because a Frictionless package doesn't have an id property) will
        #   also go to 'extras'.

    def test_ckan_round_trip_does_not_generate_empty_keywords(self):
        '''When CKAN does not have `tags`, it should not create the empty
        `keywords` list in a Frictionless package. This would lead to a round
        trip where `tags` is also not there nor empty.'''
        ckan1 = {
            "x": "yyy",
            "tags": []
        }
        exp_fd1 = {"x": "yyy"}
        fd1 = ckan_to_frictionless.dataset(ckan1)
        assert fd1 == exp_fd1
        ckan2 = frictionless_to_ckan.package(fd1)
        exp_ckan2 = {'extras': [{'key': 'x', 'value': 'yyy'}]}
        assert ckan2 == exp_ckan2
