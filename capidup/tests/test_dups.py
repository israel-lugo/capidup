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


"""Black box duplicates testing."""

import random

import pytest

import capidup.finddups as finddups

dupsdata = [
        ("", 3),
        ("a", 200),
        ("the quick brown fox jumps over the lazy dog", 2),
        ("x" * 1000000, 2),
]


def test_empty_dir(tmpdir):
    """Test that empty dirs work and produce no duplicates."""

    dups, errors = finddups.find_duplicates_in_dirs([str(tmpdir)])

    assert not errors
    assert(len(dups) == 0)


@pytest.mark.parametrize("content, dupcount", dupsdata)
def test_flat_duplicates(tmpdir, content, dupcount):
    """Test multiple duplicate files in the same directory.

    Receives a tmpdir fixture, the content to write in the duplicate files,
    and the number of duplicate files to create.

    """
    file_names = []
    for i in range(dupcount):
        basename = "file%d" % i

        f = tmpdir.join(basename)
        f.write(content)

        file_names.append(str(f))

    dups, errors = finddups.find_duplicates_in_dirs([str(tmpdir)])

    assert not errors
    assert len(dups) == 1
    assert len(dups[0]) == dupcount
    assert sorted(dups[0]) == sorted(file_names)
