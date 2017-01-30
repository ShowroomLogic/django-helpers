import os
from setuptools import find_packages, setup
from adlogic3_auth_client import __version__, __author__, __author_email__

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-helpers',
    version=__version__,
    description='Shared library of common Django helpers',
    url='https://github.com/ShowroomLogic/django-helpers',
    author=__author__,
    author_email=__author_email__,
    packages=find_packages(),
    install_requires=[
        'django-filter==0.13.0'
    ],
    zip_safe=False
)
