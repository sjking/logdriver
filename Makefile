.PHONY: clean clean-build clean-pyc clean-test coverage dist help install lint lint/flake8 lint/black
.DEFAULT_GOAL := help

export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

REQUIREMENTS_FILE := .requirements_dev.txt

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test clean-dev ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -rf dist/
	rm -rf *.egg-info/

clean-dev:
	touch ${REQUIREMENTS_FILE}
	rm ${REQUIREMENTS_FILE}

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -rf .tox/
	rm -f .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache

lint/flake8: install ## check style with flake8
	flake8 logdriver tests

lint/black: install ## check style with black
	black --check logdriver tests

lint: lint/flake8 lint/black ## check style

test: install ## run tests quickly with the default Python
	pytest

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source logdriver -m pytest
	coverage report -m
	coverage html

release: dist ## package and upload a release
	twine upload dist/*

dist: clean ## builds source and wheel package in dist directory
	python -m build

install: ## install the package to the active Python's site-packages in editable mode
	@pip list | grep logdriver > /dev/null || pip install -e .

dev-preflight:
	pip install pip-tools

dev: dev-preflight ## install the development dependencies
	ls ${REQUIREMENTS_FILE} 2> /dev/null || pip-compile --extra dev pyproject.toml --output-file ${REQUIREMENTS_FILE}
	pip install -r ${REQUIREMENTS_FILE} 2> /dev/null
	echo "Installed requirements dev"
