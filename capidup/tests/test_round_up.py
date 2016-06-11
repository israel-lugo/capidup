import sys

print sys.path

import capidup

def test_stuff():
    assert capidup.MD5_CHUNK_SIZE == 4999

