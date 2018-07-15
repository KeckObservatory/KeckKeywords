#! /usr/bin/env python
import requests

def kshow(server, keyword):
    """Show the value of a keyword

    Reproduces the behaviour of show keywords -s server

    Parameters
    ----------
    server : string
        Server to be queried
    keyword : string
        Keyword to be queried

    Returns
    -------
    value : json
         Value of the keyword

    """
    url = 'http://localhost:5002/show/%s/%s' % (server, keyword)
    response = requests.get(url)
    return response.json()


def kmodify(server, keyword, value):
    """Modify the value of a keyword.

    Reproduces the behaviour of modify -s server keyword

    Parameters
    ----------
    server : str
        Server
    keyword : str
        Keyword
    value : generic
        New value for the keyword

    Returns
    -------
    response : tuple
        Ok status and reason for failure


    """
    url = 'http://localhost:5002/modify/%s/%s' % (server, keyword)
    response = requests.post(url,json={"value": value})
    return response.ok, response.reason


def kshow_keywords(server):
    """Show the list of keywords for a given server.

    Reproduces the behaviour of show -s server keyword

    Parameters
    ----------
    server : str
        Server

    Returns
    -------
    response : array
         Array of keywords

    """
    url = 'http://localhost:5002/showkeywords/%s' % server
    response = requests.get(url)
    return response.json()

