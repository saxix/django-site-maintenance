#!/bin/sh
./setup.py sdist || exit 1


git -a tag
./setup.py sdist upload
