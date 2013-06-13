#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
 
import bit

setup(name='bit.py',
        version=bit.__version__,
        description=('This is converter bitrate for all audio files in folder.\n'
            'For example it may be audiobooks.'),
        author='Yuri Astrov',
        author_email='yuriastrov@gmail.com',
        url='https://bitbucket.org/yrain/py-bitrate/src',
        scripts=['bit.py'],
        license = 'MIT',
        entry_points = {
            'console_scripts': [
            'bit = bit:main',
            ],}
        )