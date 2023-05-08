#!/usr/bin/env python
from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='django-simple-stats',
    version='0.6.0',
    description="A django package for creating simple stats from a query",
    long_description=readme(),
    author='Serafeim Papastefanos',
    author_email='spapas@gmail.com',
    license='MIT',
    url='https://github.com/spapas/django-simple-stats',
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(exclude=['tests.*', 'tests',]),

    install_requires=['Django >= 3.0', 'six'],

    classifiers=[
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
        'Framework :: Django :: 3.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
    ],
)
