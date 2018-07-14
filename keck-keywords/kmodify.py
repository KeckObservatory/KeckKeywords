#! /usr/bin/env python

import argparse
import requests

# Parsing arguments
description = "Modify value of a keyword"
parser = argparse.ArgumentParser(description=description)
parser.add_argument('server',nargs="?",default=None, help='Server')
parser.add_argument('keyword',nargs="?",default=None, help='Keyword')
parser.add_argument('value',nargs="?",default=None, help='Value')


def kmodify(server, keyword, value):
    url = 'http://localhost:5002/modify/%s/%s' % (server, keyword)
    print("Sending %s to the server..." % value)
    response = requests.post(url,json={"value": value})
    print(response.status_code)

if __name__ == '__main__':
    
    args = parser.parse_args()
    
    kmodify(args.server, args.keyword, args.value)
