test:
	pytest -s -v test/test_*.py --doctest-modules --cov binance --cov-config=.coveragerc --cov-report term-missing

install:
	pip install -r requirement.txt -r test-requirement.txt
	pip install pandas

report:
	codecov

publish:
	python setup.py sdist upload -r pypi

.PHONY: test
