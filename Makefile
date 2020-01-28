test:
	py.test -v test/  --doctest-modules --cov binance --cov-report term-missing

.PHONY: test
