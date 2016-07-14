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


"""White box file indexing testing."""

import os
import pytest

import capidup.finddups as finddups


# Issue #12 is not fixed yet; expected to fail
@pytest.mark.xfail(raises=OSError)
def test_nonexistent(tmpdir, monkeypatch):
    """Test indexing a nonexistent directory tree.

    This test makes sure that index_files_by_size() can properly handle the
    race condition where os.walk() provides a certain filename, but when we
    try to os.lstat() it, the file is no longer there. See issue #12 for
    more details.

    Uses a tmpdir fixture to make sure the directory tree is empty, so the
    tested files really don't exist.

    """
    def fake_walk(top, topdown=True, onerror=None, followlinks=False):
        """Fake os.walk() function that returns nonexistent paths."""

        return [ (top, ['subdir1', 'subdir2'], ['file1', 'file2']) ]

    # patch finddup's os module to replace walk() with our fake_walk()
    monkeypatch.setattr(finddups.os, 'walk', fake_walk)

    d = {}
    errors = finddups.index_files_by_size(str(tmpdir), d)

    assert not d
    assert len(errors) == 2

    error_lines = '\n'.join(errors)
    for name in ('file1', 'file2'):
        assert name in error_lines
