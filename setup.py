#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import io
import re

from setuptools import setup, find_packages

RE_BADGE = re.compile(r'^\[\!\[(?P<text>.*?)\]\[(?P<badge>.*?)\]\]\[(?P<target>.*?)\]$', re.M)

BADGES_TO_KEEP = []


def md(filename):
    '''
    Load .md (markdown) file and sanitize it for PyPI.
    '''
    content = io.open(filename).read()

    for match in RE_BADGE.finditer(content):
        if match.group('badge') not in BADGES_TO_KEEP:
            content = content.replace(match.group(0), '')

    return content


def pip(filename):
    """Parse pip reqs file and transform it to setuptools requirements."""
    return open(os.path.join('requirements', filename)).readlines()


long_description = '\n'.join((
    md('README.md'),
    md('CHANGELOG.md'),
    ''
))

install_requires = pip('install.pip')
tests_require = pip('test.pip')
kerberos_require = pip('kerberos.pip')


setup(
    name='udata-ldap',
    version=__import__('udata_ldap').__version__,
    description=__import__('udata_ldap').__description__,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/opendatateam/udata-ldap',
    author='Open Data Team',
    author_email='contact@opendata.team',
    packages=find_packages(),
    include_package_data=True,
    python_requires='==2.7.*',
    install_requires=install_requires,
    setup_requires=['setuptools>=38.6.0'],
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
        'kerberos': kerberos_require,
    },
    entry_points={
        'udata.commands': [
            'ldap = udata_ldap.commands:ldap',
        ],
        'udata.plugins': [
            'ldap = udata_ldap',
        ],
    },
    license='MIT',
    zip_safe=False,
    keywords='udata LDAP',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: System :: Software Distribution',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
