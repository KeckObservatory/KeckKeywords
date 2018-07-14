#! /kroot/rel/default/bin/kpython3
import urllib.request
import argparse

# Parsing arguments
description = "Show value of a keyword"
parser = argparse.ArgumentParser(description=description)
parser.add_argument('server',nargs="?",default=None, help='Server')
parser.add_argument('keyword',nargs="?",default=None, help='Keyword')


def show(server, keyword):
    url = 'http://localhost:5002/keyword/%s/%s' % (server, keyword)
    f = urllib.request.urlopen(url)
    print(f.read().decode('utf-8'))


if __name__ == '__main__':
    
    args = parser.parse_args()
    
    show(args.server, args.keyword)
