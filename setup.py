"""Setup script for installing hugs."""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Access to Keck Instrument Keywords',
    'author': 'Luca Rizzi',
    'url': 'Project URL https://github.com/
    'download_url': 'https://github.com/jrleeman/SettingUpOpenSource',
    'author_email': 'kd5wxb@gmail.com',
    'version': '0.1',
    'install_requires': ['numpy', 'matplotlib'],
    'packages': ['hugs'],
    'scripts': [],
    'name': 'hugs'
}

setup(**config)
