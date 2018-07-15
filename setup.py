"""Setup script for installing hugs."""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import os
import glob


# Treat everything in scripts except README.rst as a script to be installed
scripts = [fname for fname in glob.glob(os.path.join('scripts', '*'))
           if os.path.basename(fname) != 'README.rst']

# Get some values from the setup.cfg
try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

conf = ConfigParser()
conf.read(['setup.cfg'])

config = {
    'description': 'Access to Keck Instrument Keywords',
    'author': 'Luca Rizzi',
    'url': 'https://github.com/KeckObservatory/KeckKeywords',
    'download_url': 'https://github.com/KeckObservatory/KeckKeywords.git',
    'author_email': 'lrizzi@keck.hawaii.edu',
    'version': '0.1',
    'install_requires': ['requests'],
    'packages': ['keck_keywords'],
    'scripts': scripts,
    'name': 'keck_keywords'
}

setup(**config)
