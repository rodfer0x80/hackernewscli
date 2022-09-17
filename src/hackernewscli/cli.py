import sys
import time
import subprocess
try:
    import pyfiglet
except:
    pass

from .configs import *
from .curl import *

#######################################
# User IO
#######################################

def banner():
    global BANNER
    print('\033c')
    if BANNER:
        ascii_banner = pyfiglet.figlet_format("Fetching HackerNews API ... \n")
    else:
        ascii_banner = "Fetching HackerNews API ...\n"
    print(ascii_banner)
    

def show_menu():
    global READS_SIZE, PAGE_SIZE
    print('\033c')
    print("******** HackerNews CLI Menu ********")
    print("")
    print(f"(x: int | x <= [1..{READS_SIZE}])  --  open read by ID")
    print(f"(&x: int | x <= [1..{READS_SIZE}])  --  open comments by ID")
    print("j[n]  --  scroll reader up .n [page limit 0] where n is number of pages to move")
    print(f"k[n]  --  scroll reader down .n [page limit {READS_SIZE//PAGE_SIZE}] where n is the numbe rof pages to move")
    print("r  --  refresh news cache")
    print("help / h  --  display help menu")
    print("quit / q  --  quit program")
    print("")
    print("********---------------------********")
    print("")
    print("")

################################
# Event Handler
################################

def hackernews_cli(data, handle):
    global TOP_NEWS, READS_SIZE, PAGE_SIZE
    if len(data) == 0:
        data = fetch_api()
    show_feed(data, handle)
    try:
        read = input(">>> ")
    except:
        print("[!] Error reading command")
        print("Type 'help' or 'h' to see help menu")
        time.sleep(1)
    if read == "quit" or read == "q":
        print("[*] Gracefully quitting ...")
        sys.exit(0)
    elif len(read) == 0:
        show_menu()
        print("[!] Invalid command\n")
        time.sleep(2)
        return data, handle
    elif read[0] == "&":
        try:
            comment = int(read[1:])
            if show_comments(data, comment) != 0:
                sys.stderr.write("[!] Read input out of bounds for data size\n")
                _ = int("IndexOutOfRange")
        except ValueError:
            show_menu()
            print("[!] Invalid command\n")
            time.sleep(2)
            return data, handle
    elif read[0] == "k":
        try:
            c = int(read[1:])
        except:
            c = 1
        handle -=  c
        if handle < 0:
            handle = 0
        return data, handle
    elif read[0] == "j" and handle < (READS_SIZE//PAGE_SIZE):
        try:
            c = int(read[1:])
        except:
            c = 1
        handle += c
        if handle > (READS_SIZE//PAGE_SIZE)-1:
            handle = (READS_SIZE//PAGE_SIZE)-1
    elif read == "r" or read == "refresh" :
        try:
            os.remove(TOP_NEWS)
        except:
            pass
        finally:
            data = fetch_api()
            return hackernews_cli(data, 0)
    elif read == "h" or read == "help":
        show_menu()
        time.sleep(2)
    else:
        try:
            read = int(read)
            if show_read(data, read) != 0:
                sys.stderr.write("[!] Read input out of bounds for data size\n")
                _ = int("IndexOutOfRange")
        except ValueError:
            show_menu()
            print("[!] Invalid command\n")
            time.sleep(2)
            return data, handle

    return data, handle

#######################################
# Open links for reads and comments
# Use brower set by flag $BROWER
#######################################

def show_comments(data, comment):
    global BROWSER, READS_SIZE, PAGE_SIZE, DATA_UNIT_SIZE
    if comment != 0:
        comments = comment*DATA_UNIT_SIZE-1
        if comment  > READS_SIZE:
            return 1
        link = data[comments]
        _, link = link.split(": ")
        if sys.platform == "darwin":
            cmd = ["open", "-a", BROWSER.capitalize(), f"{link}"]
        else: # linux
            cmd = [BROWSER, f"{link}"]
        try:
            subprocess.call(cmd)
        except:
            sys.stderr.write("[!] Error calling subprocess\n")
    return 0


# read_input <= [1..30]
# array_index_start = 0; read_input_start = 1; 
# read_space_in_lines = 5 (each read occupies 5 lines in the logfile)
# link_index = 3
def show_read(data, read):
    global BROWSER, READS_SIZE, DATA_UNIT_SIZE
    if read != 0:
        read_link = (read -1) * DATA_UNIT_SIZE + DATA_UNIT_SIZE-2
        if read > READS_SIZE:
            return 1
        link = data[read_link]
        _, link = link.split(": ")
        cmd = [BROWSER, f"{link}"]
        try:
            subprocess.call(cmd)
        except:
            sys.stderr.write("[!] Error calling subprocess\n")
    return 0


def show_feed(data, handle):
    global PAGE_SIZE, DATA_UNIT_SIZE
    print('\033c')
    i = 0
    len_data = len(data)
    for line in data[handle*PAGE_SIZE*DATA_UNIT_SIZE:(handle+1)*PAGE_SIZE*DATA_UNIT_SIZE]:
        print(line)
        i += 1
        # post block has length 5 lines 
        if i == DATA_UNIT_SIZE:
            print("\n")
            i = 0
    return 0
