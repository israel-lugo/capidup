#! /usr/bin/env python

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


"""Main CLI user interface."""

import sys
import os

import finddups


__all__ = [ 'main' ]


prog_name = "<capidup>"


def show_usage():
    """Print usage information."""

    sys.stdout.write("usage: %s <directories>...\n" % prog_name)


def main(argv):
    global prog_name

    prog_name = os.path.basename(argv[0])

    if len(argv) < 2:
        show_usage()
        sys.exit(1)

    directories_to_scan = argv[1:]

    had_errors = False
    duplicate_files_list, had_errors = finddups.find_duplicates_in_dirs(directories_to_scan)

    # sort the list of lists of duplicate files, so files in the same
    # directory show up near each other, instead of randomly scattered
    duplicate_files_list.sort()
    for duplicate_files in duplicate_files_list:
        duplicate_files.sort()
        for filename in duplicate_files:
            print filename

        print '-' * 30

    if had_errors:
        sys.stderr.write("error: some files could not be compared\n")
        sys.exit(1)



if __name__ == '__main__':
    main(sys.argv)


# vim: set expandtab smarttab shiftwidth=4 softtabstop=4 tw=75 :
