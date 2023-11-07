#!/usr/bin/python3

import os
import datetime
import urllib.request
import json
import threading
import sys
import time
import subprocess

class Cache:
    def __init__(self, cache_file=None):
        self.cache_timout_seconds = 30 * 60

        self.cache_dir = f"{os.environ['HOME']}/.cache/{__file__.split('/')[-1][:-3]}" # ~/.cache/hackernewscli
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, mode=0o700, exist_ok=True)
        
        if not cache_file:
            self.cache_file = os.path.join(self.cache_dir, "cache.txt")

        self.cache_lock = threading.Lock()  


    def clean(self):
        with self.cache_lock:
            try:
                os.remove(self.cache_file)
            except:
                pass

    def read(self):
        with self.cache_lock:
            if os.path.exists(self.cache_file):
                try:
                    with open(self.cache_file, 'r') as fp:
                        data = fp.read().splitlines()
                    new_data = [line for line in data if line != ""]
                    if len(new_data) == 0:
                        return data
                    timestamp = int(new_data[0])
                    current_time = int(time.time())
                    if current_time - timestamp <= self.cache_timout_seconds:
                        return new_data[1:]
                    else:
                        os.remove(self.cache_file)
                except Exception as e:
                    sys.stderr.write(f"[!] Error reading cache: {e}\n")
            return []

    def write(self, data):
        with self.cache_lock:
            try:
                with open(self.cache_file, "w") as fp:
                    fp.write(data)
            except Exception as e:
                sys.stderr.write(f"[!] Error writing cache: {e}\n")

class Scraper:
    def __init__(self, threads=4, http_success_code=200, data_size=80) -> None:
        self.threads = threads
        self.http_success_code = http_success_code
        self.data_size = data_size   
        self.cache = Cache()

    def __call__(self):
        data = self.cache.read()
        if data != []:
            return data
        
        res, err = self.get_call("https://hacker-news.firebaseio.com/v0/topstories.json")
        if err:
            sys.stderr.write(err)
            return []

        read_ids = res[:self.data_size]
        reads = []

        threads = []
        results_lock = threading.Lock()

        for read_id in read_ids:
            thread = threading.Thread(target=self.fetch_and_process, args=(read_id, reads, results_lock))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # filtered_reads = [read for read in reads if read['comments'].split('=')[-1] in read_ids]

        # filtered_reads.sort(key=lambda x: read_ids.index(x['comments'].split('=')[-1]))

        data = f"{int(round(time.time()))}\n"
        i = 1
        for read in reads:
            data += f"Rank: {i}\n"
            data += f"\tTitle: {read['title']}\n"
            data += f"\tTime: {read['time']}\n"
            data += f"\tLink: {read['link']}\n"
            data += f"\tComments: {read['comments']}\n"
            i += 1

        self.cache.write(data)
        return [line for line in data.splitlines() if line != ""][1:]

    def get_call(self, url):
        try:
            con = urllib.request.urlopen(url)
            res = json.load(con)
            con.close()
        except urllib.error.URLError as e:
                return "", f"[!] Connection problem, can't reach server -- {e}"
        except json.JSONDecodeError as e:
                return "", f"[!] Error decoding json -- {e}"
        return res, None
    
    def fetch_and_process(self, read_id, results, results_lock):
        url = f"https://hacker-news.firebaseio.com/v0/item/{read_id}.json"
        res, err = self.get_call(url)
        
        if not err:
            res_dict = res
            link = res_dict.get('url', "<no_link>")
            read = {
                'title': res_dict['title'],
                'time': datetime.datetime.fromtimestamp(res_dict['time']).strftime("%A, %B %d, %Y %I:%M:%S"),
                'link': link,
                'comments': f"https://news.ycombinator.com/item?id={read_id}",
            }
            
            with results_lock:
                results.append(read)

class Reader:
    def __init__(self, reads_size=80, page_size=10, data_unit_size=5):
        self.reads_size = reads_size
        self.page_size = page_size
        self.data_unit_size = data_unit_size

        self.scraper = Scraper(threads=4, http_success_code=200, data_size=self.reads_size)

    def build_banner(self):
        banner = "\033c\nFetching HackerNews API ...\n"
        return banner
    
    def build_menu(self):
        menu = (
            '\033c'
            "******** HackerNews CLI Menu ********\n"
            f"\n(x: int | x <= [1..{self.reads_size}])  --  open read by ID\n"
            f"(&x: int | x <= [1..{self.reads_size}])  --  open comments by ID\n"
            "j[n]  --  scroll reader up .n [page limit 0] where n is number of pages to move\n"
            f"k[n]  --  scroll reader down .n [page limit {self.reads_size // self.page_size}] where n is the number of pages to move\n"
            "r  --  refresh news cache\n"
            "help / h  --  display help menu\n"
            "quit / q  --  quit program\n"
            "\n********---------------------********\n"
            "\n\n"
        )
        return menu

    def run(self, data, handle):
        if len(data) == 0:
            data = self.scraper()
            if data == []:
                sys.stderr.write("[!] Error fetching data\n")
                sys.exit(-1)
        print(self.build_feed(data, handle))
        try:
            read = input(">>> ")
        except:
            print("[!] Error reading command")
            print("Type 'help' or 'h' to see the help menu")
            time.sleep(1)
        # Quit program
        if read == "quit" or read == "q" or read == "0":
            print("[*] Gracefully quitting ...")
            sys.exit(0)
        elif len(read) == 0:
            print(self.build_menu())
            return data, handle
        # Copy post link to clipboard
        elif read[0] == "&":
            try:
                comment = int(read[1:])
                if self.copy_to_clipboard(data, comment, "&") != 0:
                    sys.stderr.write("[!] Read input out of bounds for data size\n")
                    _ = int("IndexOutOfRange")
            except ValueError:
                return data, handle
        # Scroll reader left
        elif read[0] == "k":
            try:
                c = int(read[1:])
            except:
                c = 1
            handle -= c
            if handle < 0:
                handle = 0
            return data, handle
        # Scroll reader right
        elif read[0] == "j" and handle < (self.reads_size // self.page_size):
            try:
                c = int(read[1:])
            except:
                c = 1
            handle += c
            if handle > (self.reads_size // self.page_size) - 1:
                handle = (self.reads_size // self.page_size) - 1
        # Refresh cache
        elif read == "r" or read == "refresh":
            try:
                self.scraper.cache.clean()
            except:
                pass
            finally:
                data = self.scraper()
                if data == []:
                    sys.stderr.write("[!] Error fetching data\n")
                    self.scraper.cache.clean()
                return self.render(data, 0)
        # Display help menu
        elif read == "h" or read == "help":
            print(self.build_menu())
            time.sleep(2)
        # Copy read link to clipboard
        else:
            try:
                read = int(read)
                if self.copy_to_clipboard(data, read) != 0:
                    sys.stderr.write("[!] Read input out of bounds for data size\n")
                    _ = int("IndexOutOfRange")
            except ValueError:
                return data, handle
        return data, handle
    

    def copy_to_clipboard(self, data, index, mode=""):
        if index != 0:
            if mode == "&":
                index = index * self.data_unit_size - 1
            else:
                index = index * self.data_unit_size - 2
            if index > self.reads_size*self.data_unit_size:
                return 2
            link = data[index]
            _, link = link.split(": ")
            os.system(f"echo {index} {data[index]} >> ./debug.log")
            cmd = f"echo {link} | xclip -selection clipboard"
            try:
                os.system(cmd)
                return 0
            except:
                sys.stderr.write("[!] Error calling subprocess\n")
                return 3
        return 1

    def build_feed(self, data, handle):
        feed = '\033c'
        i = 0
        for line in data[handle * self.page_size * self.data_unit_size:(handle + 1) * self.page_size * self.data_unit_size]:
            feed += f"\n{line}"
            i += 1
            if i == self.data_unit_size:
                line += "\n"
                i = 0
        return feed

    def __call__(self):
        print(self.build_banner())

        data = self.scraper()
        self.scraper.cache.clean()
        if data == []:
            sys.stderr.write("[!] Error fetching data\n")
            time.sleep(2)
            return
        
        handle = 0
        while True:
            data, handle = self.run(data, handle)
            time.sleep(1)


if __name__ == "__main__":
    Reader(reads_size=80, page_size=5, data_unit_size=5)()
