# Frictionless CKAN Mapper

A library for mapping CKAN metadata <=> Frictionless metadata.

The library has zero dependencies (not even on Data Package libs). You can use it directly or use it for inspiration. Detailed outline of the algorithm is in the docs or you can read the code.

[![Travis](https://img.shields.io/travis/frictionlessdata/frictionless-ckan-mapper/master.svg)](https://travis-ci.org/frictionlessdata/frictionless-ckan-mapper)
[![Coveralls](http://img.shields.io/coveralls/frictionlessdata/frictionless-ckan-mapper/master.svg)](https://coveralls.io/r/frictionlessdata/frictionless-ckan-mapper?branch=master)
[![PyPi](https://img.shields.io/pypi/v/frictionless-ckan-mapper.svg)](https://pypi.python.org/pypi/frictionless-ckan-mapper)
[![SemVer](https://img.shields.io/badge/versions-SemVer-brightgreen.svg)](http://semver.org/)
[![Chat on Discord](https://img.shields.io/discord/695635777199145130)](https://discord.gg/2UgfM2k)

<!-- toc -->
- [Frictionless CKAN Mapper](#frictionless-ckan-mapper)
  - [Installation](#installation)
  - [Getting started](#getting-started)
  - [Reference](#reference)
    - [`ckan_to_frictionless`](#ckan_to_frictionless)
      - [`resource(ckandict)`](#resourceckandict)
      - [`dataset(ckandict)`](#datasetckandict)
    - [`frictionless_to_ckan`](#frictionless_to_ckan)
      - [`resource(fddict)`](#resourcefddict)
      - [`package(fddict)`](#packagefddict)
  - [Design](#design)
    - [CKAN reference](#ckan-reference)
    - [Algorithm: CKAN => Frictionless](#algorithm-ckan--frictionless)
    - [Algorithm: Frictionless => CKAN](#algorithm-frictionless--ckan)
  - [Developers](#developers)
    - [Install the source](#install-the-source)
    - [Run the tests](#run-the-tests)
    - [Building and publishing the package](#building-and-publishing-the-package)
      - [Build the distribution package](#build-the-distribution-package)
      - [Test the package at test.pypy.org](#test-the-package-at-testpypyorg)
      - [Tag a new Git release and publish to PyPi](#tag-a-new-git-release-and-publish-to-pypi)
<!-- tocstop -->

## Installation

- Python: install Python. The library is compatible with both Python 2.7+ and Python 3.3+.

```bash
pip install frictionless-ckan-mapper
```

**Note:** The package is installed as `frictionless-ckan-mapper` and then imported as `frictionless_ckan_mapper`.

## Getting started

```python
import frictionless_ckan_mapper

# or load from an API e.g.
# json.load(urllib.urlopen(
#     https://demo.ckan.org/api/3/package_show?id=my_dataset
# ))

ckan_dict = {
  "name": "my-dataset",
  "title": "My awesome dataset",
  "url": "http://www.example.com/data.csv"
}

from frictionless_ckan_mapper import ckan_to_frictionless as converter

out = converter.dataset(ckan_dict)

print(out)
```

## Reference

This package contains two modules:

- `frictionless_to_ckan`
- `ckan_to_frictionless`

You can import them directly like so:

```python
from frictionless_ckan_mapper import ckan_to_frictionless
from frictionless_ckan_mapper import frictionless_to_ckan
```

### `ckan_to_frictionless`

#### `resource(ckandict)`

```python
from frictionless_ckan_mapper import ckan_to_frictionless as converter

# ... Some code with a CKAN dictionary ...

output_frictionless_dict = converter.resource(ckan_dictionary)
```

#### `dataset(ckandict)`

```python
from frictionless_ckan_mapper import ckan_to_frictionless as converter

# ... Some code with a CKAN dictionary ...

output_frictionless_dict = converter.dataset(ckan_dictionary)
```

### `frictionless_to_ckan`

#### `resource(fddict)`

```python
from frictionless_ckan_mapper import frictionless_to_ckan as converter

# ... Some code with a Frictionless dictionary ...

output_ckan_dict = converter.resource(frictionless_dictionary)
```

#### `package(fddict)`

```python
from frictionless_ckan_mapper import frictionless_to_ckan as converter

# ... Some code with a Frictionless dictionary ...

output_ckan_dict = converter.package(frictionless_dictionary)
```

## Design

```text
Frictionless   <=>        CKAN
--------------------------------------
Data Package   <=>   Package (Dataset)
Data Resource  <=>   Resource
Table Schema   <=>   Data Dictionary?? (datastore resources can have schemas)
```

### CKAN reference

**Summary:**

- Class diagram below of key objects (without attributes)
- Objects with their attributes in this spreadsheet: https://docs.google.com/spreadsheets/d/1XdqGTFni5Jfs8AMbcbfsP7m11h9mOHS0eDtUZtqGVSg/edit#gid=1925460244

```mermaid
classDiagram

class Package
class Resource
class DataDictionary

Package *-- Resource
Resource o-- DataDictionary
```

![mermaid-diagram-20200703112520](https://user-images.githubusercontent.com/32682903/86486065-f9c08100-bd1f-11ea-8a1a-8f3befca0e6e.png)

Source for CKAN metadata structure:

- Dataset (Package): https://docs.ckan.org/en/2.8/api/index.html#ckan.logic.action.create.package_create
- Resource: https://docs.ckan.org/en/2.8/api/index.html#ckan.logic.action.create.resource_create

### Algorithm: CKAN => Frictionless

For Package *and* Resource

1. Expand extras into the dict.
2. Map those attributes we have known mappings for (and parse items with values e.g. a schema will be un-jsonified).
3. Drop anything we explicitly drop, e.g. `package_id` on a resource object.
4. Copy everything else over as is.

Optional extras:

- Add a profile field

### Algorithm: Frictionless => CKAN

## Developers

### Install the source

- Clone the repo:
  
  ```bash
  git clone https://github.com/frictionlessdata/frictionless-ckan-mapper.git
  ```

- And install it with pip:
  
  ```bash
  pip install -e .
  ```

### Run the tests

Use the excellent `pytest` suite as follows:

```bash
pytest tests
```

To test under both Python 2 and Python 3 environments, we use `tox`. You can run the following command:

```bash
make test
```

**Note:** Make sure that the necessary Python versions are in your environment `PATH` (Python 2.7 and Python 3.6).

### Building and publishing the package

To see a list of available commands from the `Makefile`, execute:

```bash
make list
```

#### Build the distribution package

```bash
make dist
```

Alternatively, this command will accomplish the same to build packages for both Python 2 and Python 3:

```bash
python setup.py sdist bdist_wheel --universal
```

#### Test the package at test.pypy.org

```bash
python -m twine upload --repository testpypi dist/*
```

The package will be publicly available at https://test.pypi.org/project/frictionless-ckan-mapper/ and you will be able to `pip install` it as usual.

#### Tag a new Git release and publish to PyPi

**Note:** You will need to publish from your personal PyPi account and be given access as a contributor to the project.

Make sure to update the version of the package in the file `frictionless_ckan_mapper/VERSION`. Then:

```bash
make release
```

You can quickly review the version to release with `make version`, which will print the current version stored in `VERSION`.
