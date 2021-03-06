import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'netbootmgr/README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
    name='django-netbootmgr',
    version='0.1',
    packages=['netbootmgr.hostdb', 'netbootmgr.hostdb.fixtures', 'netbootmgr.hostdb.migrations', 'netbootmgr.configstore', 'netbootmgr.configstore.migrations', 'netbootmgr.bootmgr', 'netbootmgr.bootmgr.fixtures', 'netbootmgr.bootmgr.migrations', 'netbootmgr.bootmgr.helpers', ],
    include_package_data=True,
    license='',
    description='A Network Boot Management Interface.',
    long_description=README,
    url='https://netbootmgr.dominic86.de/',
    author='Dominic Schroeder',
    author_email='dev@dominic86.de',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: NetBootManager',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
