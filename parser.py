#!/usr/bin/env python3

import sys
import json
import os
import requests

import urllib.request as urllib2
from optparse import OptionParser

def dl_image(image_url, filepath):
    img_data = requests.get(image_url).content
    with open(filepath, 'wb') as handler:
        handler.write(img_data)

def open_url(url):
    try:
        response = urllib2.urlopen(url)
    except:
        raise
    else:
        output = response.read().decode('utf-8');
        return output
    return None

def download_thread(board,thread):
    print("Parsing thread: " + thread) 

    dl_dir = 'download_dir/'
    os.makedirs(dl_dir + thread, exist_ok=True)

    url = 'http://a.4cdn.org/'+board+'/thread/'+thread+'.json'
    output = open_url(url)
    if output:
        out = json.loads(output)

        for post in out['posts']:
            try:
                tim = str(post['tim'])
                ext = str(post['ext'])
            except KeyError:
                continue
            image_url = 'http://i.4cdn.org/' + board+'/' + tim + ext
            
            filepath = dl_dir + thread + '/' + tim+ext
            if not os.path.isfile(filepath):
                print("\t" + tim + ext)
                dl_image(image_url, filepath)

def catalog_list(thread_ids, board):
    # Parse catalog thread ids
    url = 'http://a.4cdn.org/'+board+'/catalog.json'
    output = open_url(url)
    if output:
        out = json.loads(output)
        for page in out:
            for thread in page['threads']:
                thread_ids.append(thread['no'])

def archive_list(thread_ids, board):
    # Parse archive thread ids
    url = 'http://a.4cdn.org/'+board+'/archive.json'
    output = open_url(url)
    if output:
        out = json.loads(output)
        for thread in out:
            thread_ids.append(thread)

def download_threads(board, threads):
    count = 0
    size = len(threads)
    for thread in threads:
        print("[%d/%d]" % (count, size), end=" ") 
        download_thread(board, str(thread) )
        count = count + 1

def main(argv):
    parser = OptionParser()
    parser.add_option("-t", "--thread", dest="thread",
                     help="Thread number", metavar="THREAD")
    parser.add_option("-b", "--board", dest="board",
                     help="Board name", metavar="BOARD")
    parser.add_option("-a", "--archive",
                      action="store_true", dest="archive", default=False,
                      help="Parse also board's archive")

    (options, args) = parser.parse_args()
    if options.board:
        if options.thread:
            download_thread(options.board,options.thread)
        else:
            thread_ids = []
            catalog_list(thread_ids, options.board)
            if options.archive:
                archive_list(thread_ids, options.board)

            print(thread_ids)
            
            download_threads(options.board, thread_ids)
    else:
        parser.print_help()

if __name__ == '__main__':
    try:
        main(sys.argv);
    except KeyboardInterrupt:
        print('\nKeyboardInterrupt exiting')
    except:
        raise