files = binance test *.py

test:
	pytest -s -v test/test_*.py --doctest-modules --cov binance --cov-config=.coveragerc --cov-report term-missing

install:
	pip install -r requirements.txt -r test-requirements.txt
	pip install pandas

lint:
	flake8 $(files)

fix:
	autopep8 --in-place -r $(files)

report:
	codecov

build:
	rm -rf dist
	python setup.py sdist bdist_wheel

build-doc:
	sphinx-build -b html docs build_docs

publish:
	make build
	twine upload --config-file ~/.pypirc -r pypi dist/*

.PHONY: test build
