# capidup - quickly find duplicate files in directories
# Copyright (C) 2010,2014,2016 Israel G. Lugo
#
# This file is part of capidup.
#
# capidup is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# capidup is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with capidup. If not, see <http://www.gnu.org/licenses/>.
#
# For suggestions, feedback or bug reports: israel.lugo@lugosys.com


"""Unit tests for round_up_to_mult."""

import random

import pytest

import capidup.finddups as finddups


RANDOM_REPEATS=100

MAX_RANDOM_NUM=100000000002


known_values = [
    (0, 1000, 0),
    (100000000002, 100000000001, 200000000002),
    (100000000001, 100000000002, 100000000002),
    (1632479, 744829, 2234487),
]

# list of (n, n, n) tuples, with length RANDOM_REPEATS
_random_same = [
    (random.randrange(0, MAX_RANDOM_NUM),) * 3
    for _ in range(RANDOM_REPEATS)
]


# list of (n, m) tuples, with length RANDOM_REPEATS, where
# n >= 0 and m >= 1
_random_n_mult = [
    (random.randrange(0, MAX_RANDOM_NUM), random.randrange(1, MAX_RANDOM_NUM))
    for _ in range(RANDOM_REPEATS)
]


@pytest.mark.parametrize("n, mult, expected", known_values+_random_same)
def test_known_values(n, mult, expected):
    """round_up_to_mult(n, m) = e"""

    rounded = finddups.round_up_to_mult(n, mult)

    assert rounded == expected


@pytest.mark.parametrize("n, mult", _random_n_mult)
def test_invariants(n, mult):
    """round_up_to_mult(n, mult) = x, x = k*mult, x-mult <= n <= x"""

    rounded = finddups.round_up_to_mult(n, mult)

    assert rounded % mult == 0
    assert rounded - mult <= n
    assert n <= rounded

