**************************
Running the keyword server
**************************

The keyword server is Flask mini-service that must run on a host that has access to keywords.
For example, in the case of KCWI the options are kcwiserver, vm-kcwi or kcwibuild.
To produce keyword plots, the server must be able to access the keyword history. This limits the
available options and requires the server to run on selected users. For example, in the case of KCWI, the user
kcwirun@kcwiserver is authorized to connect to the history grabber.

Requirements
============

A number of packages must be available to run the keyword server:

- Flask
- Python KTL access (KTL)

If the graphics capabilities are required, to plot keywords, then these packages are required:

- pandas
- holoviews
- bokeh

If these packages are not available, the server will run anyway but no graphics will be generated.

To import KTL, there are a few options:

- use kpython3
- add the released library path to PYTHONPATH with::

    setenv PYTHONPATH /kroot/rel/default/lib/python

- make sure that the RELDIR environment variable is defined. In this case PYTHONPATH will be updated automatically.


Running the server
==================

The server is contained in keyword_server/keyword_server.py

To run it, just type::

    (k)python keyword_server.py

The script can be copied to any other directory and run from there.

Connecting to the server
========================

If the server is running on hostname, it is accessible at: http://hostname:5002.

If hostname is not accessible from your location, it is possible to establish a tunnel and then
access the localhost connection::

    ssh user@hostname -L 5002:localhost:5002

Localhost becomes the new server, so it's possible to do::

    kshow -host localhost kt1s tmp1

