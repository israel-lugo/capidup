
import random

import capidup.capidup


RANDOM_REPEATS=100

MAX_RANDOM_NUM=100000000002


def try_value(n, mult, expected):
    """round_up_to_mult(n, m) = e"""

    rounded = capidup.capidup.round_up_to_mult(n, mult)

    assert rounded == expected

def test_zero():
    """round_up_to_mult(0, x) = 0"""

    try_value(0, 1000, 0)

def test_one_above():
    """round_up_to_mult(x+1, x) = 2x"""

    try_value(100000000002, 100000000001, 200000000002)

def test_one_below():
    """round_up_to_mult(x-1, x) = x"""

    try_value(100000000001, 100000000002, 100000000002)

def test_same():
    """round_up_to_mult(x, x) = x"""

    for i in range(RANDOM_REPEATS):
        n = random.randrange(0, MAX_RANDOM_NUM)

        try_value(n, n, n)

def test_primes():
    """round_up_to_mult(p1, p2) = k*p2"""

    try_value(1632479, 744829, 2234487)

def test_generic():
    """round_up_to_mult(r1, r2) = k*r2"""

    for _ in range(RANDOM_REPEATS):
        n = random.randrange(0, MAX_RANDOM_NUM)
        mult = random.randrange(1, MAX_RANDOM_NUM)

        rounded = capidup.capidup.round_up_to_mult(n, mult)

        assert rounded % mult == 0
        assert rounded - mult <= n
        assert n <= rounded

