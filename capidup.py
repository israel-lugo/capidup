#! /usr/bin/env python

# Copyright 2010 Israel G. Lugo
# <israel.lugo@lugosys.com>

# $Id$


import sys
import os
import mmap
import hashlib


existing_files_by_md5 = {}

repeated_md5s = set()


def _print_error(error):
    """Print a listing error to stderr.

    error should be an os.OSError instance.

    """
    sys.stderr.write("error listing '%s': %s\n"
                     % (error.filename, error.strerror))



def walk_directory(root, func, func_args=[], func_kwargs={}):
    """Walk the file tree call a function for each file found.
    
    The function is given the file's full path as its first positional
    argument, followed by any positional arguments specified in the func_args
    list, and any keyword arguments specified in the func_kwargs dictionary.

    """

    # recurse into the the file tree under the specified root directory
    for curr_dir, subdirs, filenames in os.walk(root, onerror=_print_error):

        for base_filename in filenames:
            full_path = os.path.join(curr_dir, base_filename)

            # check if the filename is a regular file
            if os.path.isfile(full_path) and not os.path.islink(full_path):
                func(full_path, *func_args, **func_kwargs)



def calculate_md5(filename, max_size=0):
    """Calculate the MD5 hash of a file, or a portion of a file.

    max_size specifies the maximum amount of bytes that should be read from
    the file to calculate the MD5; a value of 0 means the whole file.

    """
    assert max_size >= 0

    file_descriptor = os.open(filename, os.O_RDONLY)

    # process the file
    try:
        file_info = os.fstat(file_descriptor)

        if file_info.st_size != 0:
            if max_size == 0:
                # we're supposed to MD5 the whole file
                md5_length = 0
            else:
                # read up to max_size bytes
                md5_length = min(length, file_info.st_size)

            try:
                # map the desired portion of the file to memory (returns
                # a string-and-file-like object)
                contents = mmap.mmap(file_descriptor, md5_length,
                                     access=mmap.ACCESS_READ)

                # calculate the MD5
                md5_summer = hashlib.md5()
                md5_summer.update(contents)
                md5 = md5_summer.digest()

            finally:
                # free the memory map
                contents.close()

        else:
            # We can't memory-map an empty file on Windows. That's ok,
            # though. We don't need to calculate the actual MD5 since we
            # know the file is empty. Just return md5(''), which is the
            # number d41d8cd98f00b204e9800998ecf8427e, represented here in
            # binary:
            md5 = '\xd4\x1d\x8c\xd9\x8f\x00\xb2\x04\xe9\x80\t\x98\xec\xf8\x42\x7e'

    finally:
        # close the file we just opened
        os.close(file_descriptor)

    return md5



def analyze_file(filename, max_size, existing_files, repeated_md5s):
    """Calculate a file's MD5 and register it as an existing file.

    Only the first max_size bytes of the file are read (or the full files if 
    If the file has a duplicate MD5, add it to the list of repeated MD5s.

    """
    try:
        md5 = calculate_md5(filename, max_size)
    except OSError, e:
        sys.stderr.write("%s: %s\n" % (e.filename, e.strerror))
        return

    if md5 not in existing_files:
        # new file, initialize the MD5 entry with a list containing only
        # this file
        existing_files[md5] = [filename]
    else:
        # we found a duplicate, append this filename to the list of files with
        # this MD5
        existing_files[md5].append(filename)

        # this MD5 has repeated files, add it to the set (it's ok if it was
        # already there, the set won't add it twice)
        repeated_md5s.add(md5)



def get_md5_repetitions(existing_files, repeated_md5s):
    """Get the list of repeated files, by MD5.
    
    Returns a list of the the lists of the names of files which are
    respectively identical among themselves (see find_identical_files for
    an example).

    """
    repeated_files = []

    for md5 in repeated_md5s:
        # get the list of files that share this MD5
        files_with_this_md5 = existing_files[md5]

        repeated_files.append(files_with_this_md5)

    return repeated_files



def find_identical_files(directories):
    """Recursively scan a list of directories, looking for identical files.
    
    The files are compared by content; their name is unimportant.

    Returns a list containing the lists of the names of files which are
    respectively identical among themselves, e.g.:
        [
          [ "file1", "copy_of_file1", "another_copy_of_file1" ],
          [ "file2", "this_is_a_copy_of_file2" ],
          [ "file3", "a_copy_of_file3", "backup_of_file3" ]
        ]

    """
    global existing_files_by_md5, repeated_md5s

    existing_files_by_md5 = {}
    repeated_md5s = set()

    for directory in directories:
        walk_directory(directory, analyze_file,
                       [0, existing_files_by_md5, repeated_md5s])

    return get_md5_repetitions(existing_files_by_md5, repeated_md5s)



def show_usage():
    sys.stdout.write("usage: %s <directories>...\n" % sys.argv[0])



if __name__ == '__main__':

    if len(sys.argv) < 2:
        show_usage()
        sys.exit(1)

    directories_to_scan = sys.argv[1:]

    repeated_files = find_identical_files(directories_to_scan)

    for equal_files in repeated_files:
        equal_files.sort()
        for filename in equal_files:
            print filename
        
        print '-' * 30
