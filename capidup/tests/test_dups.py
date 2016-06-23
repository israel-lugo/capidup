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

import pytest

import capidup.finddups as finddups

# Array of data for test_flat_find_dups_in_dirs. Each item is a tuple of
# tuples: file contents, grouped by those which are equal.
testdata = [
    (   # 1 group of 2 duplicate files
        ("a",) * 2,
    ),
    (   # 1 group of 3 empty files (considered duplicates)
        ("",) * 3,
    ),
    (   # 2 groups of dups: 3 empty files, and 200 "a" files
        ("",) * 3,
        ("a",) * 200,
    ),
    (   # 2 different files, different size
        ("foo",),
        ("foobar",),
    ),
    (   # 2 different files, same size
        ("bla",),
        ("ble",),
    ),
    (   # 2 groups of dups and 2 different files
        ("the quick brown fox jumps over the lazy dog",) * 2,
        ("The quick brown fox jumps over the lazy dog",) * 2,
        ("a",),
        ("b",),
    ),
    (   # 2 groups of large files that differ only in the last byte
        ("x" * 1000000,) * 2,
        ("x" * 999999 + "X",) * 2,
    ),
    (   # 2 groups of large files that differ only in the first byte
        ("x" * 1000000,) * 2,
        ("X" + "x" * 999999,) * 2,
    ),
]


def test_empty_dir(tmpdir):
    """Test that empty dirs work and produce no duplicates."""

    dups, errors = finddups.find_duplicates_in_dirs([str(tmpdir)])

    assert not errors
    assert(len(dups) == 0)


@pytest.mark.parametrize("file_groups", testdata)
def test_flat_find_dups_in_dirs(tmpdir, file_groups):
    """Test multiple files in the same directory.

    Receives a tmpdir fixture, and the file content to write in the
    directory. This should be a tuple of tuples: file contents, grouped by
    those which are equal. Example:

        (("a", "a"), ("b", "b"), ("c"))

    """
    name_groups = []
    group_num = 0
    for file_group in file_groups:
        names = []
        file_num = 0
        for file_content in file_group:
            basename = "g%d_file%d" % (group_num, file_num)

            f = tmpdir.join(basename)
            f.write(file_content)

            names.append(str(f))
            file_num += 1

        name_groups.append(names)
        group_num += 1

    expected_dups = [names for names in name_groups if len(names) > 1]

    dups, errors = finddups.find_duplicates_in_dirs([str(tmpdir)])

    assert not errors
    assert len(dups) == len(expected_dups)

    # the files may have been traversed in a different order from how we
    # created them; sort both lists
    dups.sort()
    expected_dups.sort()

    for i in range(len(dups)):
        assert len(dups[i]) == len(expected_dups[i])
        assert sorted(dups[i]) == sorted(expected_dups[i])

