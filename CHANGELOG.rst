CapiDup Change Log
==================

All releases and notable changes will be described here.

CapiDup adheres to `semantic versioning <http://semver.org>`_.


Unreleased__
------------
__ https://github.com/israel-lugo/capidup/compare/v1.0.1...HEAD

Added
.....

- `find_duplicates_in_dirs` can now exclude directories, through a new optional
  parameter `exclude_dirs`. See `issue #10`_.

Changed
.......

- Implement unit tests for indexing files with non-ASCII filenames, to make
  sure it works. See `issue #9`_.

Fixed
.....

- Fix possible breakage when files are deleted while they are being indexed.
  See `issue #12`_.


1.0.1_ — 2016-07-12
-------------------


First production release.


.. _issue #9: https://github.com/israel-lugo/capidup/issues/9
.. _issue #10: https://github.com/israel-lugo/capidup/issues/10
.. _issue #12: https://github.com/israel-lugo/capidup/issues/12

.. _1.0.1: https://github.com/israel-lugo/capidup/tree/v1.0.1
