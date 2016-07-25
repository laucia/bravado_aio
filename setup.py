#!/usr/bin/env python

import os

from setuptools import setup

setup(
    name="bravado-aioclient",
    version="0.0.0",
    license="BSD 3-Clause License",
    description="Library for adding Swagger support to clients and servers",
    long_description=open(os.path.join(os.path.dirname(__file__),
                                       "README.rst")).read(),
    author="",
    author_email="lauris.jullien@gmail.com",
    url="https://github.com/laucia/bravado_aio",
    packages=["bravado_aioclient"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
    ],
    install_requires=[
        "aiodns==1.0.1",
        "aiohttp==0.22.2",
        "bravado==8.1.2",
        "cchardet==1.0.0",
        "simplejson==3.8.2",
        "uvloop==0.5.0",
    ],
)
