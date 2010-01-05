#! /usr/bin/env python

import sys
import os
import mmap
import hashlib


files = {}

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
            if os.path.isfile(full_path):
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
                md5 = md5_summer.hexdigest()

            finally:
                # free the memory map
                contents.close()

        else:
            # We can't memory-map an empty file on Windows. No need to
            # calculate the actual MD5 anyway, we know the file is empty. Just
            # return md5(''), which is the following known constant:
            md5 = 'd41d8cd98f00b204e9800998ecf8427e'

    finally:
        # close the file we just opened
        os.close(file_descriptor)

    return md5



def print_md5(filename):
    try:
        print calculate_md5(filename), filename
    except OSError, e:
        sys.stderr.write("%s: %s\n" % (e.filename, e.strerror))



if __name__ == '__main__':
    walk_directory('.', print_md5)
