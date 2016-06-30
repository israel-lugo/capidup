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

import os
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

index_errors_data = range(4)
# Can't include the "1 read error" case because the file may not even be
# hashed if its size doesn't match anything else's. That's actually a nice
# test: create an unreadable file with unique size, and make sure no read
# error occurs (i.e. it wasn't hashed).
read_errors_data = [0, 2, 3, 4]


def test_empty_dir(tmpdir):
    """Test that empty dirs work and produce no duplicates."""

    dups, errors = finddups.find_duplicates_in_dirs([str(tmpdir)])

    assert not errors
    assert len(dups) == 0


def setup_flat_files(tmpdir, file_groups):
    """Create a flat file structure for testing.

    Receives a tmpdir fixture, and the file content to write in the
    directory. See test_flat_find_dups_in_dirs doc for details.

    Returns a list of groups of filenames, equal amongst themselves.

    """
    name_groups = []
    for group_num, file_group in enumerate(file_groups):
        names = []

        # create the files in this group of duplicates
        for file_num, file_content in enumerate(file_group):
            basename = "g%d_file%d" % (group_num, file_num)

            f = tmpdir.join(basename)
            f.write(file_content)

            names.append(str(f))

        name_groups.append(names)

    return name_groups


def setup_flat_dir_errors(tmpdir, count):
    """Create unreadable directories for testing.

    Receives a tmpdir fixture, and the number of unreadable directories to
    create inside it.

    Doesn't work in Windows: can't portably remove read permissions there.

    Returns a list of pathnames of the directories.

    """
    dir_errors = []
    for i in range(count):
        # create a subdirectory with no permissions
        basename = "noidx%d" % i

        d = tmpdir.mkdir(basename)
        os.chmod(str(d), 0)

        dir_errors.append(str(d))

    return dir_errors


def setup_flat_read_errors(tmpdir, count):
    """Create unreadable files for testing.

    Receives a tmpdir fixture, and the number of unreadable files to create
    inside it. The number should not be 1, as capidup may not even try to
    hash the file if there's no other file with the same size. That means
    there would be no error.

    Doesn't work in Windows: can't portably remove read permissions there.

    Returns a list of filenames.

    """
    read_errors = []
    for i in range(count):
        # create a file with no read permission
        basename = "noread%d" % i

        f = tmpdir.join(basename)
        # all error files should be the same size, to make sure they are
        # all actually hashed (if they're different sizes, they won't be)
        f.write("this will never be read")
        os.chmod(str(f), 0)

        read_errors.append(str(f))

    return read_errors


@pytest.mark.parametrize("file_groups", testdata)
@pytest.mark.parametrize("num_index_errors", index_errors_data)
@pytest.mark.parametrize("num_read_errors", read_errors_data)
def test_flat_find_dups_in_dirs(tmpdir, file_groups, num_index_errors,
                                num_read_errors):
    """Test multiple files in the same directory.

    Receives a tmpdir fixture, the file content to write in the directory,
    the number of unreadable directories to create, and the number of
    unreadable files to create.

    The file content should be a tuple of tuples: file contents, grouped by
    those which are equal. Example:

        (("a", "a"), ("b", "b"), ("c"))

    """
    # create file contents for duplicate testing
    name_groups = setup_flat_files(tmpdir, file_groups)
    # discard groups with only one file (unique files are not duplicates)
    expected_dup_groups = [names for names in name_groups if len(names) > 1]

    # create unreadable dirs and files
    index_errors = setup_flat_dir_errors(tmpdir, num_index_errors)
    read_errors = setup_flat_read_errors(tmpdir, num_read_errors)
    expected_errors = index_errors + read_errors

    # run the duplicate search
    dup_groups, errors = finddups.find_duplicates_in_dirs([str(tmpdir)])

    assert len(errors) == len(expected_errors)
    assert len(dup_groups) == len(expected_dup_groups)

    # Check that duplicate groups match. The files may have been traversed
    # in a different order from how we created them; sort both lists.
    dup_groups.sort()
    expected_dup_groups.sort()
    for i in range(len(dup_groups)):
        assert len(dup_groups[i]) == len(expected_dup_groups[i])
        assert sorted(dup_groups[i]) == sorted(expected_dup_groups[i])

    # check that all unreadable files/dirs are mentioned in the errors
    error_lines = '\n'.join(errors)
    for error_name in expected_errors:
        assert error_name in error_lines
