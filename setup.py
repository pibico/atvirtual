# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in atvirtual/__init__.py
from atvirtual import __version__ as version

setup(
	name='atvirtual',
	version=version,
	description='AT Virtual Project',
	author='PibiCo',
	author_email='pibico.sl@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
