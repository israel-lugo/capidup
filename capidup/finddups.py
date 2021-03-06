
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


"""This module implements the CapiDup public API.

Public functions:

    find_duplicates -- find duplicates in a list of files
    find_duplicates_in_dirs -- find duplicates in a list of directories

Public data attributes:

    MD5_CHUNK_SIZE -- block size for reading when calculating MD5
    PARTIAL_MD5_MAX_READ -- max size of partial read
    PARTIAL_MD5_READ_MULT -- partial read size must be a multiple of this
    PARTIAL_MD5_READ_RATIO -- how much (1/n) of a file to read in partial read
    PARTIAL_MD5_THRESHOLD -- file size above which a partial read is done

"""

import sys
import os
import stat
import hashlib
import fnmatch
import errno

from capidup import py3compat


__all__ = [ "find_duplicates", "find_duplicates_in_dirs", "MD5_CHUNK_SIZE",
        "PARTIAL_MD5_READ_MULT", "PARTIAL_MD5_THRESHOLD",
        "PARTIAL_MD5_MAX_READ", "PARTIAL_MD5_READ_RATIO" ]


MD5_CHUNK_SIZE = 512 * 1024
"""Chunk size in bytes, when reading from file to calculate MD5."""

PARTIAL_MD5_READ_MULT = 4 * 1024
"""Divisor of the partial read size, in bytes.

When hashing a portion of a file for comparison, the size of that portion
will be a multiple of this value.

.. tip:: A good choice on GNU/Linux would be multiples of page size
         (usually 4096 bytes on x86).
"""

PARTIAL_MD5_THRESHOLD = 2 * PARTIAL_MD5_READ_MULT
"""Above this file size in bytes, we do a partial comparison first."""

PARTIAL_MD5_MAX_READ = 16 * PARTIAL_MD5_READ_MULT
"""Maximum size of the partial read, in bytes."""

PARTIAL_MD5_READ_RATIO = 4
"""Partial reads of 1/n of the file size (below `PARTIAL_MD5_MAX_READ`)."""



def round_up_to_mult(n, mult):
    """Round an integer up to the next multiple."""

    return ((n + mult - 1) // mult) * mult


def should_be_excluded(name, exclude_patterns):
    """Check if a name should be excluded.

    Returns True if name matches at least one of the exclude patterns in
    the exclude_patterns list.

    """
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(name, pattern):
            return True
    return False


def prune_names(names, exclude_patterns):
    """Prune subdirs or files from an index crawl.

    This is used to control the search performed by os.walk() in
    index_files_by_size().

    names is the list of file or subdir names, to be pruned as per the
    exclude_patterns list.

    Returns a new (possibly pruned) names list.

    """
    return [x for x in names if not should_be_excluded(x, exclude_patterns)]


def filter_visited(curr_dir, subdirs, already_visited, follow_dirlinks, on_error):
    """Filter subdirs that have already been visited.

    This is used to avoid loops in the search performed by os.walk() in
    index_files_by_size.

    curr_dir is the path of the current directory, as returned by os.walk().

    subdirs is the list of subdirectories for the current directory, as
    returned by os.walk().

    already_visited is a set of tuples (st_dev, st_ino) of already
    visited directories. This set will not be modified.

    on error is a function f(OSError) -> None, to be called in case of
    error.

    Returns a tuple: the new (possibly filtered) subdirs list, and a new
    set of already visited directories, now including the subdirs.

    """
    filtered = []
    to_visit = set()
    _already_visited = already_visited.copy()

    try:
        # mark the current directory as visited, so we catch symlinks to it
        # immediately instead of after one iteration of the directory loop
        file_info = os.stat(curr_dir) if follow_dirlinks else os.lstat(curr_dir)
        _already_visited.add((file_info.st_dev, file_info.st_ino))
    except OSError as e:
        on_error(e)

    for subdir in subdirs:
        full_path = os.path.join(curr_dir, subdir)
        try:
            file_info = os.stat(full_path) if follow_dirlinks else os.lstat(full_path)
        except OSError as e:
            on_error(e)
            continue

        if not follow_dirlinks and stat.S_ISLNK(file_info.st_mode):
            # following links to dirs is disabled, ignore this one
            continue

        dev_inode = (file_info.st_dev, file_info.st_ino)
        if dev_inode not in _already_visited:
            filtered.append(subdir)
            to_visit.add(dev_inode)
        else:
            on_error(OSError(errno.ELOOP, "directory loop detected", full_path))

    return filtered, _already_visited.union(to_visit)


def index_files_by_size(root, files_by_size, exclude_dirs, exclude_files,
        follow_dirlinks):
    """Recursively index files under a root directory.

    Each regular file is added *in-place* to the files_by_size dictionary,
    according to the file size. This is a (possibly empty) dictionary of
    lists of filenames, indexed by file size.

    exclude_dirs is a list of glob patterns to exclude directories.
    exclude_files is a list of glob patterns to exclude files.

    follow_dirlinks controls whether to follow symbolic links to
    subdirectories while crawling.

    Returns True if there were any I/O errors while listing directories.

    Returns a list of error messages that occurred. If empty, there were no
    errors.

    """
    # encapsulate the value in a list, so we can modify it by reference
    # inside the auxiliary function
    errors = []
    already_visited = set()

    def _print_error(error):
        """Print a listing error to stderr.

        error should be an os.OSError instance.

        """
        # modify the outside errors value; must be encapsulated in a list,
        # because if we assign to a variable here we just create an
        # independent local copy
        msg = "error listing '%s': %s" % (error.filename, error.strerror)
        sys.stderr.write("%s\n" % msg)
        errors.append(msg)


    # XXX: The actual root may be matched by the exclude pattern. Should we
    # prune it as well?

    for curr_dir, subdirs, filenames in os.walk(root, topdown=True,
            onerror=_print_error, followlinks=follow_dirlinks):

        # modify subdirs in-place to influence os.walk
        subdirs[:] = prune_names(subdirs, exclude_dirs)
        filenames = prune_names(filenames, exclude_files)

        # remove subdirs that have already been visited; loops can happen
        # if there's a symlink loop and follow_dirlinks==True, or if
        # there's a hardlink loop (which is usually a corrupted filesystem)
        subdirs[:], already_visited = filter_visited(curr_dir, subdirs,
                already_visited, follow_dirlinks, _print_error)

        for base_filename in filenames:
            full_path = os.path.join(curr_dir, base_filename)

            # avoid race condition: file can be deleted between os.walk()
            # seeing it and us calling os.lstat()
            try:
                file_info = os.lstat(full_path)
            except OSError as e:
                _print_error(e)
                continue

            # only want regular files, not symlinks
            if stat.S_ISREG(file_info.st_mode):
                size = file_info.st_size

                if size in files_by_size:
                    # append to the list of files with the same size
                    files_by_size[size].append(full_path)
                else:
                    # start a new list for this file size
                    files_by_size[size] = [full_path]

    return errors



def calculate_md5(filename, length):
    """Calculate the MD5 hash of a file, up to length bytes.

    Returns the MD5 in its binary form, as an 8-byte string. Raises IOError
    or OSError in case of error.

    """
    assert length >= 0

    # shortcut: MD5 of an empty string is 'd41d8cd98f00b204e9800998ecf8427e',
    # represented here in binary
    if length == 0:
        return '\xd4\x1d\x8c\xd9\x8f\x00\xb2\x04\xe9\x80\t\x98\xec\xf8\x42\x7e'

    md5_summer = hashlib.md5()

    f = open(filename, 'rb')

    try:
        bytes_read = 0

        while bytes_read < length:
            chunk_size = min(MD5_CHUNK_SIZE, length - bytes_read)

            chunk = f.read(chunk_size)

            if not chunk:
                # found EOF: means length was larger than the file size, or
                # file was truncated while reading -- print warning?
                break

            md5_summer.update(chunk)

            bytes_read += len(chunk)

    finally:
        f.close()

    md5 = md5_summer.digest()

    return md5



def find_duplicates(filenames, max_size):
    """Find duplicates in a list of files, comparing up to `max_size` bytes.

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
      >>> errs
      []

    Note that ``b`` is not included in the results, as it has no duplicates.

    """
    errors = []

    # shortcut: can't have duplicates if there aren't at least 2 files
    if len(filenames) < 2:
        return [], errors

    # shortcut: if comparing 0 bytes, they're all the same
    if max_size == 0:
        return [filenames], errors

    files_by_md5 = {}

    for filename in filenames:
        try:
            md5 = calculate_md5(filename, max_size)
        except EnvironmentError as e:
            msg = "unable to calculate MD5 for '%s': %s" % (filename, e.strerror)
            sys.stderr.write("%s\n" % msg)
            errors.append(msg)
            continue

        if md5 not in files_by_md5:
            # unique beginning so far; index it on its own
            files_by_md5[md5] = [filename]
        else:
            # found a potential duplicate (same beginning)
            files_by_md5[md5].append(filename)

    # Filter out the unique files (lists of files with the same md5 that
    # only contain 1 file), and create a list of the lists of duplicates.
    # Don't use values() because on Python 2 this creates a list of all
    # values (file lists), and that may be very large.
    duplicates = [l for l in py3compat.itervalues(files_by_md5) if len(l) >= 2]

    return duplicates, errors




def find_duplicates_in_dirs(directories, exclude_dirs=None, exclude_files=None,
        follow_dirlinks=False):
    """Recursively scan a list of directories, looking for duplicate files.

    `exclude_dirs`, if provided, should be a list of glob patterns.
    Subdirectories whose names match these patterns are excluded from the
    scan.

    `exclude_files`, if provided, should be a list of glob patterns. Files
    whose names match these patterns are excluded from the scan.

    ``follow_dirlinks`` controls whether to follow symbolic links to
    subdirectories while crawling.

    Returns a 2-tuple of two values: ``(duplicate_groups, errors)``.

    `duplicate_groups` is a (possibly empty) list of lists: the names of files
    that have at least two copies, grouped together.

    `errors` is a list of error messages that occurred. If empty, there were no
    errors.

    For example, assuming ``./a1`` and ``/dir1/a2`` are identical,
    ``/dir1/c1`` and ``/dir2/c2`` are identical, ``/dir2/b`` is different
    from all others, that any subdirectories called ``tmp`` should not
    be scanned, and that files ending in ``.bak`` should be ignored:

      >>> dups, errs = find_duplicates_in_dirs(['.', '/dir1', '/dir2'], ['tmp'], ['*.bak'])
      >>> dups
      [['./a1', '/dir1/a2'], ['/dir1/c1', '/dir2/c2']]
      >>> errs
      []

    """
    if exclude_dirs is None:
        exclude_dirs = []

    if exclude_files is None:
        exclude_files = []

    errors_in_total = []
    files_by_size = {}

    # First, group all files by size
    for directory in directories:
        sub_errors = index_files_by_size(directory, files_by_size, exclude_dirs,
                                         exclude_files, follow_dirlinks)
        errors_in_total += sub_errors

    all_duplicates = []

    # Now, within each file size, check for duplicates.
    #
    # We use an iterator over the dict (which gives us the keys), instead
    # of explicitly accessing dict.keys(). On Python 2, dict.keys() returns
    # a list copy of the keys, which may be very large.
    for size in iter(files_by_size):
        # for large file sizes, divide them further into groups by matching
        # initial portion; how much of the file is used to match depends on
        # the file size
        if size >= PARTIAL_MD5_THRESHOLD:
            partial_size = min(round_up_to_mult(size // PARTIAL_MD5_READ_RATIO,
                                                PARTIAL_MD5_READ_MULT),
                               PARTIAL_MD5_MAX_READ)

            possible_duplicates_list, sub_errors = find_duplicates(files_by_size[size], partial_size)
            errors_in_total += sub_errors
        else:
            # small file size, group them all together and do full MD5s
            possible_duplicates_list = [files_by_size[size]]


        # Do full MD5 scan on suspected duplicates. calculate_md5 (and
        # therefore find_duplicates) needs to know how many bytes to scan.
        # We're using the file's size, as per stat(); this is a problem if
        # the file is growing. We'll only scan up to the size the file had
        # when we indexed. Would be better to somehow tell calculate_md5 to
        # scan until EOF (e.g. give it a negative size).
        for possible_duplicates in possible_duplicates_list:
            duplicates, sub_errors = find_duplicates(possible_duplicates, size)
            all_duplicates += duplicates
            errors_in_total += sub_errors

    return all_duplicates, errors_in_total


# vim: set expandtab smarttab shiftwidth=4 softtabstop=4 tw=75 :
