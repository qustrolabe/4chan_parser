#!/usr/bin/env python3

import sys
import json
import os
import requests

import urllib.request as urllib2
from optparse import OptionParser

import concurrent.futures

def dl_image(image_url, filepath):
    try:
        img_data = requests.get(image_url).content
    except:
        print("Error downloading file " + image_url)
    with open(filepath, 'wb') as handler:
        handler.write(img_data)

def open_url(url):
    try:
        response = urllib2.urlopen(url)
    except KeyboardInterrupt:
        raise
    except:
        # raise
        print("Error opening url: "+ url)
        return None
    else:
        output = response.read().decode('utf-8');
        return output
    return None

def download_thread(board,thread, preview=False):
    print("Parsing thread: " + thread) 

    dl_dir = 'download_dir/' + board + '/'
    os.makedirs(dl_dir + thread, exist_ok=True)

    url = 'http://a.4cdn.org/'+board+'/thread/'+thread+'.json'
    output = open_url(url)
    if output:
        out = json.loads(output)
        tasks = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for post in out['posts']:
                try:
                    tim = str(post['tim'])
                    ext = str(post['ext'])
                except KeyError:
                    continue


                dir_path = dl_dir + thread + '/'
                if not preview:
                    image_url = 'http://i.4cdn.org/' + board+'/' + tim + ext
                    filename = tim + ext
                else:
                    image_url = 'http://i.4cdn.org/' + board+'/' + tim + 's.jpg'
                    filename = tim + 's.jpg'

                filepath = dir_path + filename

                if not os.path.isfile(filepath):
                    print(filename, end=" ")
                    tasks.append( executor.submit(dl_image, image_url, filepath) )
        concurrent.futures.wait(tasks)
        print()

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

def download_threads(board, threads, preview=False):
    count = 0
    size = len(threads)
    for thread in threads:
        print("[%d/%d]" % (count, size), end=" ") 
        download_thread(board, str(thread), preview)
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

    parser.add_option("-p", "--preview",
                      action="store_true", dest="preview", default=False,
                      help="Download thumbnails (low-quality preview images *s.jpg)")

    (options, args) = parser.parse_args()
    if options.board:
        if options.thread:
            download_thread(options.board,options.thread, options.preview)
        else:
            thread_ids = []
            catalog_list(thread_ids, options.board)
            if options.archive:
                archive_list(thread_ids, options.board)

            print(thread_ids)
            
            download_threads(options.board, thread_ids, options.preview)
    else:
        parser.print_help()

if __name__ == '__main__':
    try:
        main(sys.argv);
    except KeyboardInterrupt:
        print('\nKeyboardInterrupt exiting')
    except:
        raise
