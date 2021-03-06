#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from os import path
from setuptools import setup

from kiwi_crossprepare_plugin.version import __version__

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as readme:
    long_description = readme.read()

config = {
    'name': 'kiwi_crossprepare_plugin',
    'long_description': long_description,
    'long_description_content_type': 'text/x-rst',
    'description': 'KIWI - Cross Image Arch Prepare Plugin',
    'author': 'Marcus Schaefer',
    'url': 'https://github.com/OSInside/kiwi-crossprepare-plugin',
    'download_url':
        'https://download.opensuse.org/repositories/'
        'Virtualization:/Appliances:/Builder',
    'author_email': 'ms@suse.com',
    'version': __version__,
    'license' : 'GPLv3+',
    'install_requires': [
        'docopt',
        'kiwi>=9.21.21',
        'PyYAML'
    ],
    'packages': ['kiwi_crossprepare_plugin'],
    'entry_points': {
        'kiwi.tasks': [
            'system_crossprepare=kiwi_crossprepare_plugin.tasks.system_crossprepare'
        ]
    },
    'include_package_data': True,
    'zip_safe': False,
    'classifiers': [
       # classifier: http://pypi.python.org/pypi?%3Aaction=list_classifiers
       'Development Status :: 5 - Production/Stable',
       'Intended Audience :: Developers',
       'License :: OSI Approved :: '
       'GNU General Public License v3 or later (GPLv3+)',
       'Operating System :: POSIX :: Linux',
       'Programming Language :: Python :: 3.6',
       'Programming Language :: Python :: 3.7',
       'Topic :: System :: Operating System',
    ]
}

setup(**config)
