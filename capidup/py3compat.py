
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

"""Python 2/3 compatibility module.

Public members:

    itervalues: get an iterator over a dict's values
    iteritems: get an iterator over a dict's (key, value) items

"""

# Dictionary helper functions. Definitions from PEP469 (public domain)
try:
    dict.iteritems
except AttributeError:  # pragma: no cover
    # Python 3
    def itervalues(d):
        """Get an iterator over the values of d."""
        return iter(d.values())
    def iteritems(d):
        """Get an iterator over the (key, value) items of d."""
        return iter(d.items())
else:                   # pragma: no cover
    # Python 2
    def itervalues(d):
        """Get an iterator over the values of d."""
        return d.itervalues()
    def iteritems(d):
        """Get an iterator over the (key, value) items of d."""
        return d.iteritems()
