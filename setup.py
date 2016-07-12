
"""Package information for capidup."""

from setuptools import setup

from capidup.version import __version__

def read_file(path):
    """Read a file and return its entire contents."""

    with open(path, 'r') as f:
        return f.read()

setup(
    name='capidup',
    description='Quickly find duplicate files in directories',
    author="Israel G. Lugo",
    author_email='israel.lugo@lugosys.com',
    url='https://github.com/israel-lugo/capidup',
    version=__version__,
    packages=['capidup',],
    license='GPLv3+',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Filesystems',
    ],
    long_description=read_file('README.rst'),
)
