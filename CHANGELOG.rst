CapiDup Change Log
==================

All releases and notable changes will be described here.

CapiDup adheres to `semantic versioning <http://semver.org>`_. In short, this
means the version numbers follow a three-part scheme: *major version*, *minor
version* and *patch number*.

The *major version* is incremented for releases that break compatibility, such
as removing or altering existing functionality. The *minor version* is
incremented for releases that add new visible features, but are still backwards
compatible. The *patch number* is incremented for minor changes such as bug
fixes, that don't change the public interface.


Unreleased__
------------
__ https://github.com/israel-lugo/capidup/compare/v1.1.0...HEAD


1.1.0_ — 2017-02-06
-------------------

Added
.....

- `find_duplicates_in_dirs` can now exclude directories, through a new optional
  parameter `exclude_dirs`. See `issue #10`_.

- `find_duplicates_in_dirs` can now exclude files, through a new optional
  parameter `exclude_files`. See `issue #15`_.

- `find_duplicates_in_dirs` can now follow symbolic links to subdirectories,
  through a new optional parameter `follow_dirlinks`. See `issue #16`_.

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
.. _issue #15: https://github.com/israel-lugo/capidup/issues/15
.. _issue #16: https://github.com/israel-lugo/capidup/issues/16

.. _1.1.0: https://github.com/israel-lugo/capidup/tree/v1.1.0
.. _1.0.1: https://github.com/israel-lugo/capidup/tree/v1.0.1
