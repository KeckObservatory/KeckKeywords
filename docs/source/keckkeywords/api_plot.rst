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

Plots
=====

It is possible to plot the history of the last day for a keyword with:

    http://hostname:5002/plot/<server>/<keyword>

Note that the plot is dynamic: you can pan and zoom.

