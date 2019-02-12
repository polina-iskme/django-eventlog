#!/usr/bin/env python
#
from os import path
from setuptools import setup

NAME = "django-eventlog"
VERSION = "1.0.0"

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), "rb") as fobj:
    long_description = fobj.read().decode('utf-8')

setup(
    name=NAME,
    version=VERSION,
    description="Django middleware for asynchronous event logging",
    long_description=long_description,
    author="Steve Schoettler",
    author_email="email@example.com",
    url="http://example.com",
    license="MIT",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Database',
        'Topic :: Internet :: Log Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Logging',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    keywords="django eventlog logging asynchronous logstash fluent pubsub",
    packages=["django_eventlog"],
    package_dir={"": "src"},
    install_requires=[
        "django>=1.10,<2.0",
        "eventlog",
    ],
    dependency_links=[
        "https://github.com/iskme/eventlog/tarball/master#egg=eventlog",
    ],
)
