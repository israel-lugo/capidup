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

.. function:: capidup.finddups.find_duplicates(filenames, max_size)

   Find duplicates in a list of files, comparing up to `max_size` bytes.

   Returns a 2-tuple of two values: ``(duplicate_groups, errors)``.

   `duplicate_groups` is a (possibly empty) list of lists: the names of
   files that have at least two copies, grouped together.

   `errors` is a list of error messages that occurred. If empty, there were
   no errors.

   For example, assuming ``a1`` and ``a2`` are identical, ``c1`` and ``c2`` are
   identical, and ``b`` is different from all others::

     >>> dups, errs = find_duplicates(['a1', 'a2', 'b', 'c1', 'c2'], 1024)
     >>> dups
     [['a1', 'a2'], ['c1', 'c2']]
     >>> errors
     []

   Note that `b` is not included in the results, as it has no duplicates.


.. function:: capidup.finddups.find_duplicates_in_dirs(directories)

   Recursively scan a list of directories, looking for duplicate files.

   Returns a 2-tuple of two values: ``(duplicate_groups, errors)``.

   `duplicate_groups` is a (possibly empty) list of lists: the names of files
   that have at least two copies, grouped together.

   `errors` is a list of error messages that occurred. If empty, there were no
   errors.

   For example, assuming ``./a1`` and ``dir1/a2`` are identical, ``dir1/c1`` and
   ``dir2/c2`` are identical, and ``dir2/b`` is different from all others:

     >>> dups, errs = find_duplicates(['.', 'dir1', 'dir2'])
     >>> dups
     [['./a1', 'dir1/a2'], ['dir1/c1', 'dir2/c2']]
     >>> errors
     []


Public data members
...................

.. data:: capidup.finddups.MD5_CHUNK_SIZE

   Chunk size in bytes, for reading the file while calulating MD5.

.. data:: capidup.finddups.PARTIAL_MD5_MAX_READ

   Maximum size of the partial read, in bytes.

.. data:: capidup.finddups.PARTIAL_MD5_READ_MULT
   
   Multiple (in bytes) for the partial read size.

.. tip:: GNU/Linux should be faster when reading multiples of page size
   (usually 4096 bytes on x86).

.. data:: capidup.finddups.PARTIAL_MD5_READ_RATIO

   Maximum size of the partial read, in bytes.

.. data:: capidup.finddups.PARTIAL_MD5_THRESHOLD

   Minimum file size, in bytes, above which we do partial comparison before
   trying the full thing.

