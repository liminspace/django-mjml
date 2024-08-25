.PHONY: install lint test build publish

install:
	pip install -U pip \
 && pip install -U -r requirements.dev.txt

lint:
	pre-commit run -a

test:
	DJANGO_SETTINGS_MODULE=tests.settings PYTHONWARNINGS=always coverage run -m django test \
 && coverage report

build:
	rm -rf dist/ \
 && hatch build

publish:
	hatch publish
