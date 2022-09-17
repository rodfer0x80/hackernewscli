# Bootstrap file
import sys
import os

from . import *


def runme():
    # System
    os.umask(~0o700) # linux mask 700
    try:
        os.system("echo 'test' > /tep/hn_cli_test.txt && rm -f /tmp/hn_cli_test.txt")
    except:
        sys.stderr.write("[!] Script needs read and write permission to /tmp\n")
        sys.exit(1)
    os.system("mkdir -p /tmp/hackernewscli")


    handle  = 0
    data = check_cache()
    
    banner()
    time.sleep(1)
    
    while True:
        data, handle = hackernews_cli(data, handle)
    
    return 0


if __name__ == '__main__':
    runme()
