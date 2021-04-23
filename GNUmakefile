SHELL := $(shell which bash)
.SHELLFLAGS = -xeuEo pipefail -c
.ONESHELL:

.PHONY: clean build publish

clean:
	rm -rf build dist || true

build: clean
	python setup.py sdist bdist_wheel

publish:
	python -m twine upload dist/*
