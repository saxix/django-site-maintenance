#!/bin/sh

git -a tag
./setup.py sdist upload
