#!/usr/bin/env bash

PACKAGE_PATH="$(dirname "$0")/.."
cd $PACKAGE_PATH
export PYTHONPATH=$PYTHONPATH:$PACKAGE_PATH

coverage erase
coverage run --source=a3grpc -m unittest discover
coverage html --title="a3grpc coverage report"
python -m webbrowser ./htmlcov/index.html
