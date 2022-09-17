import sys
import time
import datetime
import requests

from .configs import *

#######################################
# Make GET calls to fetch API
# Parse data 
# Cache and read from cache
#######################################

def get_call(url):
    global HTTP_SUCCESS
    err = False
    try:
        res = requests.get(url)
    except Exception as e:
        sys.stderr.write(f"[!] Connection problem, can't reach API -- {e}\n")
        sys.exit(4)
    if res.status_code != HTTP_SUCCESS:
        err = True
        return f"[x] Response status code: {res.status_code} -- ", err
    return res, err


def process_response(res):
    global READS_SIZE
    read_ids = res.json()
    reads = list()
    for read_id in read_ids[:READS_SIZE]:
        url = f"https://hacker-news.firebaseio.com/v0/item/{read_id}.json"
        res, err = get_call(url)
        if not err:
            res_dict = res.json()
            try:
                link = res_dict['url']
            except:
                link = "<no_link>"
            read = {
                    'title': res_dict['title'],
                    'time': datetime.datetime.fromtimestamp(res_dict['time']).strftime("%A, %B %d, %Y %I:%M:%S"),
                    'link': link,
                    'comments': f"https://news.ycombinator.com/item?id={read_id}",
            }
            reads.append(read)
        else:
            sys.stderr.write(err)
    return reads


def fetch_api():
    global TOP_NEWS
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    res, err = get_call(url)
    if err:
        sys.stderr.write(res)
        sys.exit(5)
    # multithread for each each and write to cache file using mutex
    # then read file, remove timestamp and return to cli inteface
    reads = process_response(res)
    timestamp = int(round(time.time()))
    data = f"{timestamp}\n"
    i = 1
    for read in reads:
        data += f"Rank: {i}\n"
        data += f"\tTitle: {read['title']}\n"
        data += f"\tTime: {read['time']}\n"
        data += f"\tLink: {read['link']}\n"
        data += f"\tComments: {read['comments']}\n"
        i += 1
    new_data = list()
    with open(TOP_NEWS, "w") as fp:
        fp.write(data)
    for line in data.splitlines():
        if line != "":
            new_data.append(line)
    return new_data[1:]
