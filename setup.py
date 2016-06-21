
"""Package information for capidup."""

from setuptools import setup

# get __version__
exec(compile(open('capidup/version.py').read(), 'capidup/version.py', 'exec'))

setup(
    name='capidup',
    description='Quickly find duplicate files in directories',
    author="Israel G. Lugo",
    author_email='israel.lugo@lugosys.com',
    version=__version__,
    packages=['capidup',],
    entry_points={
        'console_scripts': [ 'capidup=capidup.cli:main' ],
    },
    license='License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    long_description="""
Capidup recursively crawls through all the files in a list of directories and
identifies duplicate files. Duplicate files are files with the exact same
content, regardless of their name, location or timestamp.

This program is designed to be quite fast. It uses a smart algorithm to detect
and group duplicate files using a single pass on each file (that is, Capidup
doesn't need to compare each file to every other).

"""
)
