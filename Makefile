PYTHON := python
PIP := pip
GIT := git

BUILD_DIR := build
DIST_DIR := dist
SENTINELS := .make-cache

SOURCE_FILES := $(shell find ./frictionless_ckan_mapper -type f -name "*.py")

PACKAGE := $(shell grep '^PACKAGE =' setup.py | cut -d "'" -f2)
VERSION := $(shell head -n 1 $(PACKAGE)/VERSION)

.PHONY: all dist distclean install list release test version

## Clean all generated files
distclean:
	rm -rf $(BUILD_DIR) $(DIST_DIR)
	rm -rf $(SENTINELS)/dist

## Create distribution files to upload to pypi
dist: $(SENTINELS)/dist



all: list

install:
	pip install --upgrade -e .[develop]

list:
	@grep '^\.PHONY' Makefile | cut -d' ' -f2- | tr ' ' '\n'

# Upload a release of the package to PyPi and create a Git tag
# Note: Travis CI will upload on tag push.
release: $(SENTINELS)/dist
	@echo
	@echo "You are about to release authoritative version $(VERSION)"
	@echo "This will:"
	@echo " - Create a git tag release-$(VERSION)"
	@echo " - Create a release package and upload it to PyPi via Travis CI"
	$(GIT) tag release-$(VERSION)
	$(GIT) push --tags
# $(PYTHON) -m twine upload dist/*

$(SENTINELS):
	mkdir $@

$(SENTINELS)/dist-setup: | $(SENTINELS)
	$(PIP) install -U pip wheel twine
	@touch $@

$(SENTINELS)/dist: $(SENTINELS)/dist-setup $(DIST_DIR)/frictionless-ckan-mapper-$(VERSION).tar.gz $(DIST_DIR)/frictionless-ckan-mapper-$(VERSION)-py2.py3-none-any.whl | $(SENTINELS)
	@touch $@

$(DIST_DIR)/frictionless-ckan-mapper-$(VERSION).tar.gz $(DIST_DIR)/frictionless-ckan-mapper-$(VERSION)-py2.py3-none-any.whl: $(SOURCE_FILES) setup.py | $(SENTINELS)/dist-setup
	$(PYTHON) setup.py sdist bdist_wheel --universal

test:
	pylama $(PACKAGE)
	tox

version:
	@echo $(VERSION)
