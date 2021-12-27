#!/usr/bin/env python

import requests
import concurrent.futures
import collections
from .check import check_site
from .dirscan import Scan
from .fuzzer import Fuzz
import chardet


class dirStrike:
    def __init__(self, ip, wordlist, mode, threads, ext):
        self.ip = ip
        self.wordlist = wordlist
        self.ext = ext
        self.threads = threads
        self.q = collections.deque()
        self.directories = []
        self.mode = mode
        self.res = check_site()
        self.code = [404, None]

    def dirStrike(self):
        file = open(self.wordlist, 'rb')
        file_read = file.readlines()
        for Dir in file_read:
            detect = chardet.detect(Dir)['encoding']
            if detect == 'ascii':
                DIR = Dir.decode(detect)
                if not DIR.startswith('#') and DIR != '':
                    self.q.append(DIR.strip('\n\r'))

        test_code = requests.get(self.ip+'/non-existent-site-abcdefghijkblabla', allow_redirects=False).status_code
        print('done:',test_code)
        if test_code != 404:
            self.code[1] = test_code

        if self.mode == 'dir':
            scan = Scan(self.ip, self.ext, self.code)
            with concurrent.futures.ThreadPoolExecutor(max_workers=int(self.threads)) as executor:
            	result = executor.map(scan.dirscan, self.q)

        elif self.mode == 'fuzz':
            fuzz = Fuzz(self.ip, self.code)
            with concurrent.futures.ThreadPoolExecutor(max_workers=int(self.threads)) as executor:
            	result = executor.map(fuzz.fuzzer, self.q)
