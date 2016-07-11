=================
 capidup package
=================

Quickly find duplicate files in directories.

CapiDup recursively crawls through all the files in a list of directories and
identifies duplicate files. Duplicate files are files with the exact same
content, regardless of their name, location or timestamp.

This package is designed to be quite fast. It uses a smart algorithm to detect
and group duplicate files using a single pass on each file (that is, CapiDup
doesn't need to compare each file to every other).


capidup.finddups module
-----------------------
.. module:: capidup.finddups

This module implements the public API. The rest is just for internal use by the
package.

Public functions
................

.. autofunction:: capidup.finddups.find_duplicates

.. autofunction:: capidup.finddups.find_duplicates_in_dirs


Public data members
...................

.. autodata:: capidup.finddups.MD5_CHUNK_SIZE

.. autodata:: capidup.finddups.PARTIAL_MD5_READ_MULT

.. autodata:: capidup.finddups.PARTIAL_MD5_THRESHOLD

.. autodata:: capidup.finddups.PARTIAL_MD5_MAX_READ

.. autodata:: capidup.finddups.PARTIAL_MD5_READ_RATIO
