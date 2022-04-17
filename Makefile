SHELL:=/usr/bin/env bash

lint_python:
	flake8 .
	#mypy .

lint_django:
	# check migrations graph
	python manage.py makemigrations --dry-run --check
	# run django check
	python manage.py check --fail-level=WARNING

unit:
	pytest --dead-fixtures --dup-fixtures
	pytest \
		--cov=. \
		--junitxml=.tests_reports/junit.xml

lint_package:
	poetry check
	# TODO: fix `importlib-metadata` dependency issues
	# pip check
	# TODO: check in few days if numpy security fix was made
	safety check -i 44715 --bare --full-report

test: \
	lint_python \
	lint_django \
	unit \
	lint_package
