import os
import sys
import time

from .configs import *

def check_cache():
    global TOP_NEWS, CACHE_TIMEOUT_SECONDS
    if os.path.exists(TOP_NEWS):
        with open(TOP_NEWS, 'r') as fp:
            data = fp.read().splitlines()
        new_data = list()
        for line in data:
            if line != "":
                new_data.append(line)
        if len(new_data) == 0:
            sys.stderr.write("[!] Error parsing tempfile\n")
            return data
        data = new_data
        try:
            timestamp = int(data[0])
        except ValueError:
            sys.stderr.write("[!] Error reading tempfile timestamp\n")
            return data
        try:
            cw = int(round(time.time()))
        except:
            sys.stderr.write("[!] Error with system clock\n")
            sys.exit(6)
        if cw - timestamp > CACHE_TIMEOUT_SECONDS:
            os.remove(TOP_NEWS)
            return list()
        return data[1:]
    return list()
