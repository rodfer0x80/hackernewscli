#!/bin/sh
test -e ./venv ||\
    python3 -m venv venv &&\
    source ./venv/bin/activate &&\
    pip install --upgrade pip &&\
    test -e ./requirements.txt &&\
    pip install -r ./requirements.txt

source ./venv/bin/activate &&\
    python ./__main__.py

