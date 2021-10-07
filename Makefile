#
# Settings
#

SOURCE_FILES = *.py
LINTER_CONFIGS = https://git.confirm.ch/confirm/development-guidelines/raw/master/configs
PYPI_INDEX = https://pypi.confirm.ch/

#
# Cleanup
#

clean: clean-cache clean-test clean-venv

clean-cache:
	find . -name '__pycache__' -delete

clean-test:
	rm -vf .coverage coveragerc .isort.cfg .pylintrc tox.ini

clean-venv:
	rm -vrf .venv

#
# Install
#

venv:
	python3 -m venv .venv

develop: install
	pip3 install -i $(PYPI_INDEX) -r requirements-dev.txt

install:
	pip3 install -r requirements.txt

#
# Development
#

isort:
	curl -sSfLo .isort.cfg $(LINTER_CONFIGS)/isort.cfg
	isort $(SOURCE_FILES)

#
# Test
#

test-commits:
	git tools validate

test-isort:
	curl -sSfLo .isort.cfg $(LINTER_CONFIGS)/isort.cfg
	isort -c --diff $(SOURCE_FILES)

test-pycodestyle:
	curl -sSfLo tox.ini $(LINTER_CONFIGS)/tox.ini
	pycodestyle $(SOURCE_FILES)

test-pylint:
	curl -sSfLo .pylintrc $(LINTER_CONFIGS)/pylintrc
	pylint $(SOURCE_FILES)

test: test-isort test-pycodestyle test-pylint
