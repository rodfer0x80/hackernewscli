#!/usr/bin/env python3

import os
import sys


def main():
    pwd = '/'.join(__file__.split("/")[:-2])
    if pwd[-1] == ".":
        pwd = pwd[:-1]
    pwd = f"{pwd}/src"
    ls = os.listdir(pwd)
    if "venv" not in ls:
        os.system(f"python3 -m venv {pwd}/venv &&\
                    source {pwd}/venv/bin/activate &&\
                    pip install --upgrade pip &&\
                    pip install -r {pwd}/requirements.txt")
    os.system(f"source {pwd}/venv/bin/activate &&\
                python {pwd}/__main__.py")
    return 0

if __name__ == '__main__':
    sys.exit(main())
