import random
import pytest

from binance.common.sequenced_list import SequencedList


@pytest.fixture
def l():  # noqa:E743
    return SequencedList([
        (x, random.randint(0, 100)) for x in range(0, 10)
    ])


def test_add_to_first(l):
    assert l.add((-1, 10)) == (0, False)

    assert l[0] == (-1, 10)


def test_add_overridden(l):
    assert l.add((0, 2)) == (0, True)

    assert l[0] == (0, 2)


def test_zero_quantity(l):
    assert l.add((1, 0)) == (1, True)

    # The original l[1] has been removed
    assert l[1][0] == 2
    assert len(l) == 9


def test_add_last(l):
    assert l.add((100, 100)) == (10, False)
    assert l[10] == (100, 100)
    assert len(l) == 11


def test_zero_quantity_price_non_exists(l):
    origin_quantity = l[0][1]

    assert l.add((- 1, 0)) == (0, False)
    assert l[0][1] == origin_quantity


def test_add_to_last(l):
    assert l.add((101, 1)) == (10, False)
    assert l[10][0] == 101
