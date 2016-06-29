
# CapiDup - quickly find duplicate files in directories
# Copyright (C) 2010,2014,2016 Israel G. Lugo
#
# This file is part of CapiDup.
#
# CapiDup is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# CapiDup is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with CapiDup. If not, see <http://www.gnu.org/licenses/>.
#
# For suggestions, feedback or bug reports: israel.lugo@lugosys.com


"""Quickly find duplicate files in directories.

CapiDup recursively crawls through all the files in a list of directories and
identifies duplicate files. Duplicate files are files with the exact same
content, regardless of their name, location or timestamp.

This package is designed to be quite fast. It uses a smart algorithm to detect
and group duplicate files using a single pass on each file (that is, CapiDup
doesn't need to compare each file to every other).

The useful API is in capidup.finddups. The rest is just for internal use by
the package.

"""


