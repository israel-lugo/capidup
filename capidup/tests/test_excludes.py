# vim: set fileencoding=utf-8 :

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


"""Black box exclusion testing."""

import os
import functools
import pytest

import capidup.finddups as finddups


reference_file="referencefile"


# Array of data for test_exclude_dirs and test_exclude_files. Each item is
# a tuple of lists: dirs/files to create, exclude patterns, and expected
# dirs/files (not matched by the pattern).
exclude_data = [
    # no exclude pattern returns all results
    (["a", "b", "c"], [], ["a", "b", "c"]),
    # exclude pattern that doesn't match
    (["a", "b", "c"], ["x"], ["a", "b", "c"]),
    # no subdirs, exclude pattern doesn't break
    ([], ["a"], []),
    # basic exclude one directory
    (["a", "b", "c"], ["a"], ["b", "c"]),
    # exclude character range
    (["a", "b", "c"], ["[ab]"], ["c"]),
    # exclude negative range
    (["a", "b", "c", "xx"], ["[!ac]"], ["a", "c", "xx"]),
    # two exclude patterns
    (["a", "b", "c"], ["a", "b"], ["c"]),
    # pattern only excludes full matches
    (["a", "b", "aa", "bb", "xx"], ["[ab]"], ["aa", "bb", "xx"]),
    # * with range prefix
    (["a", "b", "aa", "bb", "xx"], ["[ab]*"], ["xx"]),
    # * excludes everything
    (["a", "b", "aa", "bb", "xx"], ["*"], []),
    # ? matches any character
    (["a", "b", "xy", "xz"], ["x?"], ["a", "b"]),
    # exclude extension (*.bak)
    (["a.txt", "a.bak", "abak", "a.bak.txt"], ["*.bak"], ["a.txt", "abak", "a.bak.txt"]),
    # exclude extension with no prefix name
    (["a.txt", ".tmp", "a.tmp", ".txt"], ["*.tmp"], ["a.txt", ".txt"]),
]


def unnest_sequence(seq):
    """[[a, b], [c, d]] -> [a, b, c, d]

    Receives a sequence of sequences (e.g. list of lists), and returns a
    new sequence of the same type, with one level of nesting removed.

    The sequence must be concatenable (it must support the 'add' operator).
    It must also be homogeneous: all elements of the sequence must be a
    sequence of the same type as their parent. A corollary of this is that
    all elements of the sequence must be nested at least one level.

    """
    class_ = type(seq)

    return functools.reduce(class_.__add__, seq, class_())


@pytest.mark.parametrize("exclude_dirs_info", exclude_data)
def test_exclude_dirs(tmpdir, exclude_dirs_info):
    """Test excluding directories.

    Receives a tmpdir fixture and a tuple (dirs, exclude_dirs,
    expected_dirs).

    Creates the specified subdirectories, and places two identical files in
    each one. Then calls find_duplicates_in_dirs with the specified exclude
    pattern. Any directory not excluded will be detected due to the
    duplicate files.

    """
    dirs, exclude_dirs, expected_dirs = exclude_dirs_info

    # Create a tree of the specified directories, and place two identical
    # files in each directory (a1 and a2).
    for d in dirs:
        tmpdir.mkdir(d)

        for fname in ["a1", "a2"]:
            f = tmpdir.join(d, fname)
            f.write("a")

    dup_groups, errors = finddups.find_duplicates_in_dirs([str(tmpdir)], exclude_dirs=exclude_dirs)

    assert not errors

    flattened_files = unnest_sequence(dup_groups)

    # generate a list (without repetitions) of the subdirs in the results
    result_dirs = []
    prefix_len = len(str(tmpdir)) + len(os.path.sep)
    for path in flattened_files:
        # get subdir, from something like /path/to/tmpdir/subdir/file
        subdir = path[prefix_len:].partition(os.path.sep)[0]

        # subdirs appear once for every file; eliminate repetitions
        if subdir not in result_dirs:
            result_dirs.append(subdir)

    expected_dirs.sort()
    result_dirs.sort()
    assert result_dirs == expected_dirs


@pytest.mark.parametrize("exclude_files_info", exclude_data)
def test_exclude_files(tmpdir, exclude_files_info):
    """Test excluding files.

    Receives a tmpdir fixture and a tuple (files, exclude_files,
    expected_files).

    Creates the specified files, all identical, plus a reference file to
    serve as comparison with them. Then calls find_duplicates_in_dirs with
    the specified exclude pattern. Any file not excluded will be detected
    as a duplicate of the reference file.

    The global variable reference_file contains the name of the reference
    file to be created. The files to create should not contain this name,
    to avoid collisions.

    """
    files, exclude_files, expected_files = exclude_files_info

    # create the files, all identical
    for fname in [reference_file,] + files:
        f = tmpdir.join(fname)
        f.write("a")

    dup_groups, errors = finddups.find_duplicates_in_dirs([str(tmpdir)], exclude_files=exclude_files)

    assert not errors

    if not expected_files:
        assert not dup_groups

    else:
        assert len(dup_groups) == 1

        prefix_len = len(str(tmpdir)) + len(os.path.sep)

        result_files = [path[prefix_len:].partition(os.path.sep)[0] for path in dup_groups[0]]
        result_files.remove(reference_file)

        expected_files.sort()
        result_files.sort()
        assert result_files == expected_files
