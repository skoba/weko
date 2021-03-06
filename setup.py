# -*- coding: utf-8 -*-
#
# This file is part of WEKO3.
# Copyright (C) 2017 National Institute of Informatics.
#
# WEKO3 is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# WEKO3 is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WEKO3; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.

"""Weko module platform."""

import os
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'check-manifest>=0.25',
    'coverage>=4.0',
    'isort>=4.2.2',
    'pydocstyle>=1.0.0',
    'pytest-cache>=1.0',
    'pytest-cov>=1.8.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.0',
]

invenio_db_version = '>=1.0.0b3,<1.1.0'

extras_require = {
    # Flavours
    'ils': [
        'invenio-app-ils>=1.0.0.dev0,<1.1.0',
    ],
    # Bundles
    'base': [
        'invenio-admin>=1.0.0b1,<1.1.0',
        'invenio-assets>=1.0.0b6,<1.1.0',
        'invenio-formatter>=1.0.0b1,<1.1.0',
        'invenio-logging>=1.0.0b1,<1.1.0',
        'invenio-mail>=1.0.0b1,<1.1.0',
        'invenio-rest>=1.0.0a10,<1.1.0',
        'invenio-theme>=1.0.0b1,<1.1.0',
    ],
    'auth': [
        'invenio-access>=1.0.0a11,<1.1.0',
        'invenio-accounts>=1.0.0b1,<1.1.0',
        'invenio-oauth2server>=1.0.0a14,<1.1.0',
        'invenio-oauthclient>=1.0.0a12,<1.1.0',
        'invenio-userprofiles>=1.0.0a9,<1.1.0',
    ],
    'metadata': [
        'invenio-indexer>=1.0.0a9,<1.1.0',
        'invenio-jsonschemas>=1.0.0a3,<1.1.0',
        'invenio-oaiserver>=1.0.0a12,<1.1.0',
        'invenio-pidstore>=1.0.0b1,<1.1.0',
        'invenio-records-rest>=1.0.0a18,<1.1.0',
        'invenio-records-ui>=1.0.0a8,<1.1.0',
        'invenio-records>=1.0.0b1,<1.1.0',
        'invenio-search-ui>=1.0.0a6,<1.1.0',
        'invenio-search>=1.0.0a9,<1.1.0',
    ],
    # Databases
    'mysql': [
        'invenio-db[mysql]' + invenio_db_version,
    ],
    'postgresql': [
        'invenio-db[postgresql]' + invenio_db_version,
    ],
    # Elasticsearch version
    'elasticsearch6': [
        'elasticsearch>=6.0.0,<7.0.0',
        'elasticsearch-dsl>=6.0.0,<6.2.0',
     ],

    # Docs and test dependencies
    'docs': [
        'Sphinx>=1.5.1',
    ],
    'tests': tests_require,
}

#
# Aliases allow for easy installation of a specific type of Weko instances.
#   pip install weko[repository]
#
aliases = {

}

for name, requires in aliases.items():
    extras_require[name] = []
    for r in requires:
        extras_require[name].extend(
            extras_require[r] if r in extras_require else [r]
        )

# All alias to install every possible dependency.
extras_require['all'] = []
for name, reqs in extras_require.items():
    if name in {'mysql', 'postgresql'}:
        continue
    extras_require['all'].extend(reqs)

#
# Minimal required packages for an Weko instance (basically just the
# Flask application loading).
#
setup_requires = [
    'pytest-runner>=2.6.2',
]

install_requires = [
    'Flask>=0.11.1',
    'citeproc-py-styles>=0.1.1',
    'citeproc-py>=0.4.0',
    'datacite>=1.0.1',
    'invenio-base>=1.0.0a14,<1.1.0',
    'invenio-celery>=1.0.0b2,<1.1.0',
    'invenio-config>=1.0.0b2,<1.1.0',
    'invenio-i18n>=1.0.0b3,<1.1.0',
    'invenio-csl-rest>=1.0.0a1',
    'fpdf>=1.7.2',
    'Pillow>=5.4.1',
    'resync==1.0.9'
]

packages = find_packages()

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('invenio', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='invenio',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='Invenio digital library framework',
    license='GPLv2',
    author='National Institute of Informatics',
    author_email='wekosoftware@nii.ac.jp',
    url='https://github.com/wekosoftware/weko',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={},
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 3 - Alpha',
    ],
)
