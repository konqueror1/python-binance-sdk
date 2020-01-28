test:
	py.test -v test/  --doctest-modules --cov binance --cov-report term-missing

install:
	pip install -r requirement.txt -r test-requirement.txt

report:
	codecov

.PHONY: test
