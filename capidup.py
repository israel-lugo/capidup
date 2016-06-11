#! /usr/bin/env python

# capidup - quickly find duplicate files in directories
# Copyright (C) 2010,2014 Israel G. Lugo
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


"""Quickly find duplicate files in directories.

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


__all__ = [ "find_duplicates", "find_duplicates_in_dirs", "MD5_CHUNK_SIZE",
        "PARTIAL_MD5_READ_MULT", "PARTIAL_MD5_THRESHOLD",
        "PARTIAL_MD5_MAX_READ", "PARTIAL_MD5_READ_RATIO" ]


# Chunk size in bytes, for reading file while calculating MD5
MD5_CHUNK_SIZE = 512 * 1024

# Multiple (in bytes) for the partial read size (4096, the usual page
# size for x86 on GNU/Linux and Windows, seems a good choice: GNU/Linux
# seems to do faster when reading multiples of page size)
PARTIAL_MD5_READ_MULT = 4 * 1024

# Minimum file size, in bytes, above which we do a partial comparison before
# trying the full thing
PARTIAL_MD5_THRESHOLD = 2 * PARTIAL_MD5_READ_MULT

# Maximum size of the partial read, in bytes
PARTIAL_MD5_MAX_READ = 16 * PARTIAL_MD5_READ_MULT

# How much of the file to read in a partial read (divider applied to the
# file's size). Up to PARTIAL_MD5_MAX_READ
PARTIAL_MD5_READ_RATIO = 4



def _print_error(error):
    """Print a listing error to stderr.

    error should be an os.OSError instance.

    """
    sys.stderr.write("error listing '%s': %s\n"
                     % (error.filename, error.strerror))



def round_up_to_mult(n, mult):
    """Round an integer up to the next multiple."""

    return ((n + mult - 1) // mult) * mult



def index_files(root, files_by_size):
    """Recursively index files under a root directory.

    Each regular file is added *in-place* to the files_by_size dictionary,
    according to the file size. This is a (possibly empty) dictionary of
    lists of filenames, indexed by file size.

    """
    for curr_dir, _, filenames in os.walk(root, onerror=_print_error):

        for base_filename in filenames:
            full_path = os.path.join(curr_dir, base_filename)

            file_info = os.lstat(full_path)

            # only want regular files, not symlinks
            if stat.S_ISREG(file_info.st_mode):
                size = file_info.st_size

                if size in files_by_size:
                    # append to the list of files with the same size
                    files_by_size[size].append(full_path)
                else:
                    # start a new list for this file size
                    files_by_size[size] = [full_path]



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

    f = open(filename, 'r')

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
    """Find duplicates in a list of files, comparing up to max_size bytes.

    Returns a (possibly empty) list of the lists of names of files which
    are respectively identical among themselves (see find_duplicates_in_dirs
    for an example).

    """
    global _errors_while_comparing

    # shortcut: can't have duplicates if there aren't at least 2 files
    if len(filenames) < 2:
        return []

    # shortcut: if comparing 0 bytes, they're all the same
    if max_size == 0:
        return [filenames]

    files_by_md5 = {}

    for filename in filenames:
        try:
            md5 = calculate_md5(filename, max_size)
        except EnvironmentError as e:
            sys.stderr.write("unable to calculate MD5 for '%s': %s\n"
                             % (filename, e.strerror))
            _errors_while_comparing = True
            continue

        if md5 not in files_by_md5:
            # unique beginning so far; index it on its own
            files_by_md5[md5] = [filename]
        else:
            # found a potential duplicate (same beginning)
            files_by_md5[md5].append(filename)

    # Filter out the unique files (lists of files with the same md5 that
    # only contain 1 file), and create a list of the lists of duplicates.
    # Use itervalues() instead of values() to save memory, by not copying
    # the entire (potentially very large) list of values in files_by_md5.
    duplicates = [l for l in files_by_md5.itervalues() if len(l) >= 2]

    return duplicates




def find_duplicates_in_dirs(directories):
    """Recursively scan a list of directories, looking for duplicate files.

    The files are compared by content; their name is unimportant.

    Returns a list containing the lists of the names of files which are
    respectively identical among themselves, e.g.:
        [
          [ "file1", "copy_of_file1", "another_copy_of_file1" ],
          [ "file2", "this_is_a_copy_of_file2" ],
          [ "file3", "a_copy_of_file3", "backup_of_file3" ]
        ]

    """
    files_by_size = {}

    # First, group all files by size
    for directory in directories:
        index_files(directory, files_by_size)

    all_duplicates = []

    # Now, within each file size, check for duplicates. There are a couple
    # of memory optimizations here:
    #
    # 1. We iterate over the dictionary's keys (file sizes) and get the
    # value (file list) from the dictionary when we need it, instead of
    # expanding directly to (size, file list). This is to avoid having to
    # keep the (potentially very large) file list for the entire duration
    # inside the for. Inside the for we're already creating a temp list
    # which may potentially be very large (possible_duplicates_list), and
    # adding some of that to all_duplicates. We don't want to keep the
    # original file list around longer than necessary.
    #
    # 2. We use iterkeys() to iterate the keys (file sizes), instead of
    # keys(). keys() returns a new list of keys, which may be very large,
    # whereas iterkeys() iterates over the dictionary's existing keys.
    for size in files_by_size.iterkeys():
        # for large file sizes, divide them further into groups by matching
        # initial portion; how much of the file is used to match depends on
        # the file size
        if size >= PARTIAL_MD5_THRESHOLD:
            partial_size = min(round_up_to_mult(size // PARTIAL_MD5_READ_RATIO,
                                                PARTIAL_MD5_READ_MULT),
                               PARTIAL_MD5_MAX_READ)

            possible_duplicates_list = find_duplicates(files_by_size[size], partial_size)
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
            all_duplicates += find_duplicates(possible_duplicates, size)

    return all_duplicates



def show_usage():
    """Print usage information."""

    sys.stdout.write("usage: %s <directories>...\n" % sys.argv[0])



if __name__ == '__main__':

    # this is updated by find_duplicates in case of errors while comparing
    _errors_while_comparing = False

    if len(sys.argv) < 2:
        show_usage()
        sys.exit(1)

    directories_to_scan = sys.argv[1:]

    duplicate_files_list = find_duplicates_in_dirs(directories_to_scan)

    # sort the list of lists of duplicate files, so files in the same
    # directory show up near each other, instead of randomly scattered
    duplicate_files_list.sort()
    for duplicate_files in duplicate_files_list:
        duplicate_files.sort()
        for filename in duplicate_files:
            print filename

        print '-' * 30

    if _errors_while_comparing:
        sys.stderr.write("error: some files could not be compared\n")
        sys.exit(1)


# vim: set expandtab smarttab shiftwidth=4 softtabstop=4 tw=75 :
