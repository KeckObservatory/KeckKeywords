***********
Basic Usage
***********

Important note
==============

The Flask Keyword server must be running on the host computer to be able to access keywords.

Command line access
===================

The commands are similar to the show/modify commands available on instrument servers, but with a 'k' in front.
Because this package can run on any computer, it needs to know which instrument host or other host to connect to.
This is specified with the option -host. For example, to get the tmp1 keyword from the kt1s server on KCWI, use::

    kshow -host kcwiserver kt1s tmp1

A keyword can be modified using::

    kmodify -host kcwiserver kbds object "Feige110"

The list of keywords for a server can be obtained with::

    kshowkeywords -host kcwiserver kbgs

Permanently specify the default host
====================================

If you are mostly using a single instrument, it is convenient to permanently specify the host to connect to.
This is done by creating a file called .config/keckkeywords.ini in your home directory. The file should contain
the following lines::

    [keckkeywords]
    host = kcwiserver

A simple way to create such a file is to run the kshow command without specifying a host::

    kshow kt1s tmp1

If the configuration file doesn't exist, KeckKeywords will not show the keyword and report an error, but it will
also create a default configuration file that can be edited.


