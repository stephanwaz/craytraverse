.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
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

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr var/
	rm -fr dist/
	rm -fr .eggs/
	rm -rf _skbuild/
	# find . -name '*.egg-info' -exec rm -fr {} +
	# find . -name '*.egg' -exec rm -f {} +
	find . -name '*.o' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find craytraverse/
	 -name '*.pyc' -exec rm -f {} +
	find craytraverse/
	 -name '*.pyo' -exec rm -f {} +
	find craytraverse/
	 -name '*~' -exec rm -f {} +
	find craytraverse/
	 -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage*
	rm -fr htmlcov/
	rm -fr .pytest_cache

test: ## run tests quickly with the default Python
	py.test

dist: clean ## builds source and wheel package
	python setup.py sdist bdist_wheel
	ls -l dist

log:
	git log --graph --all --date=short --pretty=tformat:"%w(80,0,20)%C(auto)%h %C(red bold)%ad:%C(auto)%d%n%w(80,8,8)%s"
