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


"""Black box duplicates testing, simple tests."""

import pytest

import capidup.finddups as finddups


# Python3.2 doesn't support u"" string literals (3.3 and onward do, for
# backwards compatibility). To support 3.2, we must avoid u"". We use
# native literals (byte str on Python 2, str on Python 3), and use a
# transparent wrapper to decode them on Python 2. We rely on the source
# file being encoded in UTF-8.
try:
    unicode
except NameError:
    def u(s):
        """Return s as-is.

        This is a transparent wrapper for declaring Unicode strings without
        the u"" prefix in a Python version-independent way.

        """
        return s
else:
    def u(s):
        """Decode s as an UTF-8 string.

        This is a transparent wrapper for declaring Unicode strings without
        the u"" prefix in a Python version-independent way.

        """
        return unicode(s, 'utf-8')


weird_filenames = [
    u('archælogy'), u('cão'), u('15€'), u('µs'), u('Straße'), u('søster'),
    u('я тебе кохаю'), u('tabs\tare\tus'), u('你好')
]


def test_empty_dir(tmpdir):
    """Test that empty dirs work and produce no duplicates."""

    dups, errors = finddups.find_duplicates_in_dirs([str(tmpdir)])

    assert not errors
    assert len(dups) == 0


@pytest.mark.parametrize("filename", weird_filenames)
def test_weird_filenames(tmpdir, filename):
    """Test that weird filenames don't cause breakage."""

    othername = 'x' if filename != 'x' else 'xx'

    # create the weird filenames
    f1 = tmpdir.join(filename)
    f1.write("a")
    f2 = tmpdir.join(othername)
    f2.write("a")

    dups, errors = finddups.find_duplicates_in_dirs([str(tmpdir)])

    assert not errors
    assert len(dups) == 1
    assert len(dups[0]) == 2
    # We don't check if the filenames match; that may lead to issues since
    # we'd have to decode for comparison (the test would introduce problems
    # that the original program doesn't have).

