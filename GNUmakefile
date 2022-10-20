SHELL := $(shell which bash)
.SHELLFLAGS = -xeuEo pipefail -c
.ONESHELL:

.PHONY: clean build publish

clean:
	rm -rf build dist || true

# see https://realpython.com/pypi-publish-python-package/#build-your-package
build: clean
	poetry build

# see https://realpython.com/pypi-publish-python-package/#upload-your-package
# poetry config http-basic.pypi __token__ pypi-<api-token>
publish: build
	poetry publish
