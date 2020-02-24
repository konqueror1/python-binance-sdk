test:
	pytest -s -v test/test_*.py --doctest-modules --cov binance --cov-config=.coveragerc --cov-report term-missing

install:
	pip install -r requirement.txt -r test-requirement.txt
	pip install pandas

report:
	codecov

build: binance
	rm -rf dist
	python setup.py sdist bdist_wheel

build-doc:
	sphinx-build -b html docs build_docs

publish:
	make build
	twine upload --config-file ~/.pypirc -r pypi dist/*

.PHONY: test
