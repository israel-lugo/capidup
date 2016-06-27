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


"""Test package version number validity."""

import re

import capidup.version

# From PEP440, public version identifiers MUST comply with the following:
# [N!]N(.N)*[{a|b|rc}N][.postN][.devN]

version_re_str = r'^(?:\d+!)?\d+(?:\.\d+)*(?:(?:a|b|rc)\d+)?(?:\.post\d+)?(?:\.dev\d+)?$'

version_re = re.compile(version_re_str, re.IGNORECASE)

def test_version_defined():
    """Make sure __version__ is defined and non-empty."""

    assert hasattr(capidup.version, '__version__')
    assert capidup.version.__version__

def test_version_number():
    """Make sure __version__ is sintactically valid, as per PEP440."""

    m = version_re.match(capidup.version.__version__)

    assert m is not None
