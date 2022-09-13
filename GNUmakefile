SHELL := $(shell which bash)
.SHELLFLAGS = -xeuEo pipefail -c
.ONESHELL:

.PHONY: clean build publish

clean:
	rm -rf build dist || true

# see https://realpython.com/pypi-publish-python-package/#build-your-package
build: clean
	python -m build

# see https://realpython.com/pypi-publish-python-package/#upload-your-package
publish:
	python -m twine check dist/*
	python -m twine upload dist/*
