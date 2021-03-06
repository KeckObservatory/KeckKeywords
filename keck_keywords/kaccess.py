#! /usr/bin/env python
import requests
import configparser
import os
import sys
import webbrowser

def kshow(host, server, keyword):
    """Show the value of a keyword

    Reproduces the behaviour of show keywords -s server

    Parameters
    ----------
    host : str
        Instrument host computer
    server : str
        Server to be queried
    keyword : str
        Keyword to be queried

    Returns
    -------
    value : json
         Value of the keyword

    """
    url = 'http://%s:5002/show/%s/%s' % (host, server, keyword)
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        print("Error: %s.\nCheck that the Flask keyword server is running." % str(e))
        return
    return response.json()


def kmodify(host, server, keyword, value):
    """Modify the value of a keyword.

    Reproduces the behaviour of modify -s server keyword

    Parameters
    ----------
    host : str
        Instrument host computer
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
    url = 'http://%s:5002/modify/%s/%s' % (host, server, keyword)
    try:
        response = requests.post(url,json={"value": value})
    except requests.exceptions.RequestException as e:
        print("Error: %s.\nCheck that the Flask keyword server is running." % str(e))
        return
    return response.ok, response.reason


def kshow_keywords(host, server):
    """Show the list of keywords for a given server.

    Reproduces the behaviour of show -s server keyword

    Parameters
    ----------
    host : str
        Instrument host computer
    server : str
        Server

    Returns
    -------
    response : array
         Array of keywords

    """
    url = 'http://%s:5002/showkeywords/%s' % (host, server)
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        print("Error: %s.\nCheck that the Flask keyword server is running." % str(e))
        return
    return response.json()

def kplot(host, server, keyword):
    """ Plot a day worth of value for the specified keyword

    Parameters
    ----------
    host : str
        Instrument host computer
    server : str
        Server
    keyword
        Keyword
    """

    url = 'http://%s:5002/plot/%s/%s' % (host, server, keyword)
    webbrowser.open(url)

def kstream(host, server, keyword):
    """Streams values and plots a keyword (EXPERIMENTAL, only works on localhost)

    Parameters
    ----------
    host : str
        Instrument host
    server : str
        Server
    keyword : str
        Keyword
    """
    url = 'http://%s:5002/teststream/%s/%s' % (host, server, keyword)
    webbrowser.open(url)

def kstop(host):
    """Stop the monitoring of the currently streamed keyword

    Parameters
    ----------
    host : str
        Instrument host
    """
    url = 'http://%s:5002/stop' % (host)
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        print("Error: %s.\nCheck that the Flask keyword server is running." % str(e))
        return
    return response.json()

def get_host(args):

    if args.host:
        host = args.host
    else:
        config = parse_config()
        host = config['keckkeywords']['host']
    return host

def parse_config():
    config = configparser.ConfigParser()
    user_config_dir = os.path.expanduser("~") + "/.config"
    user_config = user_config_dir + "/keckkeywords.ini"

    # Just a small function to write the file
    def write_file():
        config.write(open(user_config, 'w'))

    if not os.path.exists(user_config):
        print("No -host option specified and no configuration file found")
        print("A default config file will be created in your home directory")
        config['keckkeywords'] = {'host': 'localhost'}

        write_file()
        sys.exit(1)
    else:
        # Read File
        config.read(user_config)

        try:
            config.get('keckkeywords', 'host')
            return config
        except configparser.NoOptionError:
            print("No option called 'host' in your configuration file")
