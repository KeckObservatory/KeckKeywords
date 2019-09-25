********************
API access and plots
********************


API access to the keywords
==========================

If the server is running, you can use a browser to directly access the keywords by visiting the following routes:

- kshow:

    http://hostname:5002/show/<server>/<keyword>

- kmodify:

    http://hostname:5002/modify/<server>/<keyword>?value=<value>

- kshowkeywords:

    http://hostname:5002/showkeywords/<server>

- kplot:

    http://hostname:5002/plot/<server>/<keyword>

Plots
=====

It is possible to plot the history of the last day for a keyword with:

    http://hostname:5002/plot/<server>/<keyword>

Note that the plot is dynamic: you can pan and zoom.

If both ports 5002 and 5006 are forwarded to localhost or are open, it is possible to plot a live stream for a keyword::

    http://hostmame:5002/teststream/<server>/<keyword>

Note that the stream should be stopped by accessing::

    http://hostname:5002/stop

This interrupts the remote monitoring of the keyword

