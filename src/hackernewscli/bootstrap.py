# Bootstrap file
import sys


from . import *
#from example import example


def runme():
    # System
    os.umask(~0o700) # linux mask 700
    try:
        os.system("echo 'test' > /tep/hn_cli_test.txt && rm -f /tmp/hn_cli_test.txt")
    except:
        sys.stderr.write("[!] Script needs read and write permission to /tmp\n")
        sys.exit(1)
    os.system("mkdir -p /tmp/hackernews")
    TOP_NEWS = "/tmp/hackernews/hackernews_cli.txt"
    READS_SIZE = 80
    PAGE_SIZE = 4

    # Web
    HTTP_SUCCESS = 200
    try:
        BROWSER = os.environ['BROWSER']
    except KeyError:
        sys.stderr.write("[!] Flag $BROWSER not set\n")
        sys.exit(2)
    #
    #                         # Cache
    #                         # DATA_UNIT_SIZE represents the size of a block of data from the API
    #                         # each read maps to 5 key:value of information about the read
    #                         # -5:rank,
    #                         # -4:title,
    #                         # -3:time, 
    #                         # -2:link, 
    #                         # -1:comments
    #                         # so to access values decrement variable
    #                         DATA_UNIT_SIZE = 5
    #                         CACHE_TIMEOUT_SECONDS = 30 * 60
    #                         try:
    #                             CACHE_TIMEOUT_SECONDS = int(CACHE_TIMEOUT_SECONDS)
    #                             except:
    #                                 sys.stderr.write("[!] CACHE_TIMEOUT_SECONDS must be and integer of seconds\n")
    #                                     sys.exit(3)
    #
    return 0

