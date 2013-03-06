#!/usr/bin/env python
import os
from distutils.core import setup, Command
from distutils.command.register import register
from distutils.command.upload import upload

from distutils.command.install import INSTALL_SCHEMES
import sys

dirname = 'maintenance'

app = __import__(dirname)

VERSIONMAP = {'final': (app.VERSION, 'Development Status :: 5 - Production/Stable'),
              'rc': (app.VERSION, 'Development Status :: 4 - Beta'),
              'beta': (app.VERSION, 'Development Status :: 4 - Beta'),
              'alpha': ('master', 'Development Status :: 3 - Alpha'), }

download_tag, development_status = VERSIONMAP[app.VERSION[3]]

for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']


def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


def scan_dir(target, _packages=None, _data_files=None):
    packages = _packages or []
    data_files = _data_files or []
    for dir_path, dir_names, file_names in os.walk(target):
        # Ignore dir_names that start with '.'
        for i, dir_name in enumerate(dir_names):
            if dir_name.startswith('.'):
                del dir_names[i]
        if '__init__.py' in file_names:
            packages.append('.'.join(fullsplit(dir_path)))
        elif file_names:
            data_files.append([dir_path, [os.path.join(dir_path, f) for f in file_names]])
    return packages, data_files

packages, data_files = scan_dir(dirname)


def process_requirements(filename):
    urls, pkgs = [], []
    with open(filename) as fd:
        for line in fd.read().splitlines():
            line = line.strip()
            if line.startswith('-i'):
                urls.append(line.split()[1])
            elif line.startswith('http://') or line.startswith('https://'):
                urls.append(line)
                pkgs.append(os.path.basename(line))
            elif line.startswith('-f'):
                urls.append(line.split()[1])
            elif line.startswith('-r'):
                include_file = line.split()[1]
                a, b = process_requirements(os.path.join(os.path.dirname(filename), include_file))
                urls.extend(a)
                pkgs.extend(b)
            elif line.startswith('#'):
                pass
            else:
                pkgs.append(line)
    return pkgs, urls

dependencies, dependency_links = process_requirements('requirements.txt')

setup(
    name=app.NAME,
    version=app.get_version(),
    url='https://github.com/saxix/%s' % app.NAME,
    download_url='http://pypi.python.org/packages/source/d/{app}/{app}-{ver}.tar.gz' % {'app':app.NAME, 'ver':app.get_version()},
    author='Stefano Apostolico',
    author_email='s.apostolico@gmail.com',
    license="MIT License",
    packages=packages,
    data_files=data_files,
    platforms=['linux'],
    install_requires=dependencies,
    dependency_links=dependency_links,
    classifiers=[
        development_status,
        'Environment :: Web Environment',
        'Framework :: Django',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Developers']
)
