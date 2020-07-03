# -*- coding: utf-8 -*-

import os
import io
from setuptools import setup, find_packages


# Helpers
def read(*paths):
    """Read a text file."""
    basedir = os.path.dirname(__file__)
    fullpath = os.path.join(basedir, *paths)
    contents = io.open(fullpath, encoding='utf-8').read().strip()
    return contents


# Prepare
PACKAGE = 'frictionless_ckan_mapper'
NAME = PACKAGE.replace('_', '-')
INSTALL_REQUIRES = [
    'six>=1.9,<2.0'
]
TESTS_REQUIRE = [
    'pylama',
    'tox'
]
README = read('README.md')
VERSION = read(PACKAGE, 'VERSION')
PACKAGES = find_packages(exclude=['examples', 'tests'])


# Run
setup(
    name=NAME,
    version=VERSION,
    packages=PACKAGES,
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
    extras_require={'develop': TESTS_REQUIRE},
    zip_safe=False,
    long_description=README,
    long_description_content_type='text/markdown',
    description='A library for mapping CKAN metadata <=> Frictionless metadata.',
    author='Open Knowledge International',
    url='https://github.com/frictionlessdata/frictionless_ckan_mapper',
    copyright='Copyright 2020 (c) Viderum Inc. / Datopian',
    license='MIT',
    keywords=[
        'data',
        'ckan',
        'frictionless',
        'conversion',
        'package',
        'dataset',
        'resource'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
