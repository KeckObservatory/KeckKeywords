from flask import Flask, json, jsonify, request, render_template
import subprocess
import sys
import os
import warnings
from datetime import datetime
import time
from math import pi
from threading import Thread

if 'RELDIR' in os.environ:
    sys.path.append('%s/lib/python' % os.environ['RELDIR'])
else:
    warnings.warn("The RELDIR variable is not defined. It might not be possible to import KTL")
try:
    import ktl
except ImportError as error:
    print("KTL cannot be imported. The keyword server cannot be started.")
    print("Make sure RELDIR is defined or add the ktl location to your PYTHONPATH")
    print(error)
    #sys.exit(1)
use_graphics = True
try:
    import pandas as pd
    import holoviews as hv
    from holoviews.streams import Buffer
    from bokeh.embed import file_html, server_document
    from bokeh.resources import CDN
    from bokeh.plotting import curdoc, figure
    from bokeh.models import ColumnDataSource, AjaxDataSource, DatetimeTickFormatter, Slider
    from bokeh.server.server import Server
    from bokeh.layouts import column
    from bokeh.themes import Theme

    from tornado import gen
    from tornado.ioloop import IOLoop
    from threading import Thread, enumerate
    from functools import partial
    from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature

except ImportError as error:
    use_graphics = False
    warnings.warn("One of the graphics modules is not available. Graphics functions are disabled.")
    print(error)

global stop_signal
stop_signal = False
global stream_server
global stream_keyword

app = Flask(__name__)


def json_load(data):
    return json.loads(data)


def json_dump(data):
    return json.dumps(data)


def json_pretty(data):
    return json.dumps(data, sort_keys=True, indent=4)


@app.route('/show/<server>/<keyword>')
def show_keyword(server, keyword):
    mykeyword = ktl.cache(server, keyword)
    value = mykeyword.read()
    return json_dump(value)


@app.route('/modify/<server>/<keyword>', methods=['POST','PUT'])
def modify_keyword(server, keyword):
    mykeyword = ktl.cache(server,keyword)
    print("Is it json:" + str(request.is_json))
    content = request.get_json()
    print("Request data: %s" % (str(content)))
    mykeyword.write(content['value'])
    new_value = mykeyword.read()
    return json_dump(new_value)


@app.route('/showkeywords/<server>')
def show_keywords(server):
    cmd = 'show keywords -s %s' % (server)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    output = output.decode().splitlines()
    return jsonify(output)


def generate_history(server, keyword, date_range):
    cmd = "gshow -s %s %s -terse -date '%s'" % (server, keyword, date_range)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    output = output.decode().splitlines()
    #print(output)
    p_status = p.wait()
    mykeyword = ktl.cache(server, keyword)
    mykeyword.monitor()

    mydata = pd.DataFrame(columns=['time','value'])
    for line in output:
        #print(str(line))
        if "#" in line:
            continue
        mydata = mydata.append({
            'time': datetime.strptime(line.split()[0], "%Y-%m-%dT%H:%M:%S.%f"),
            'value': float(line.split()[1])
             }, ignore_index=True)
    return mydata


@app.route('/plot/<server>/<keyword>')
def plot_keyword(server, keyword):
    useBokeh = True
    useHV = False
    if use_graphics is False:
        return json_dump("The graphics system is disabled")
    hv.extension('bokeh')
    mydata = generate_history(server, keyword, '1 day ago')
    mykeyword = ktl.cache(server,keyword)
    units = mykeyword['units']

    # pure bokeh solution
    if useBokeh:
        source = ColumnDataSource(mydata)
        #print(source)
        print(mydata.head())
        p = figure(x_axis_type='datetime', plot_width=800, plot_height=500, title='Keyword plot: %s' % str(keyword).capitalize())
        p.circle(x='time', y='value',source=source)
        p.xaxis.axis_label = 'Time'
        p.yaxis.axis_label = '%s (%s) (%s)' % (str(keyword).capitalize(), str(server).capitalize(), str(units))
        p.xaxis.major_label_orientation = pi/4
        p.xaxis.formatter = DatetimeTickFormatter(
            hours=["%d %B %Y"],
            days=["%d %B %Y"],
            months=["%d %B %Y"],
            years=["%d %B %Y"],
        )
        html = file_html(p, CDN, "my plot")
        return html

    # pyviz solution generating pure html
    if useHV:
    #renderer = hv.plotting.mpl.MPL.Renderer.instance(dpi=120)
        renderer = hv.renderer('bokeh')
        myplot = hv.Points(mydata).options(width=800, height=500,xrotation=90, size=5)
        myplot = myplot.redim.label(time='Time', value="%s (%s)" % (str(keyword).capitalize(), str(server).capitalize()))
        myplot = myplot.relabel('Keyword plot: %s' % str(keyword).capitalize())
        myplot = myplot.redim.unit(value=str(units))
        hvplot = renderer.get_plot(myplot).state
        html = file_html(hvplot, CDN, "Plot: %s from %s" % (keyword, server))
        return html
    #script = file_html(hvplot, CDN, 'myplot')
    #html = renderer._figure_data(hvplot)
    #html = renderer.get_plot(myplot).state
    #print(curve)
    #script,div = components(p)

    #return render_template("plot.html", keyword_name = keyword, the_div=div, the_script=script)
    #print(html)
    #return html

######## STREAM TESTING


@app.route('/stop')
def stop_stream():
    global stop_signal
    for t in enumerate():
        print(t.getName())
    stop_signal = True
    return json_dump("stop")


def keyword_stream(doc):
    mykeyword = ktl.cache(stream_server, stream_keyword)

    def convert_time(timestamp):
        return datetime.fromtimestamp(timestamp)  # .strptime('%Y-%m-%d %H:%M:%S.%f')

    global example
    mydata = generate_history(stream_server, stream_keyword, '10 minutes ago')
    #example = pd.DataFrame(
    #    {'x': [convert_time(time.time())],
    #     'y': [initial_y]},
    #    columns=['x', 'y'])
    example = mydata
    dfstream = Buffer(example, length=100, index=False)
    curve_dmap = hv.DynamicMap(hv.Points, streams=[dfstream]).options(color='red', line_width=5, width=800, height=500, xrotation=90)

    # doc = curdoc()

    @gen.coroutine
    def update(x, y):
        print("Update called")
        global example
        example = example.append({'time': x, 'value': y}, ignore_index=True)
        # html = file_html(hvplot, CDN, "Plot: %s from %s" % (keyword, server))
        # return html

        dfstream.send(example)
        # print(example.head())

    def callback(keyword):
        print("call back called")
        y = keyword.binary
        print("y:" + str(y))
        time_now = keyword.timestamp
        print("timestamp:" + str(time_now))
        last_time_stamp = example.iloc[-1]['time']
        print(last_time_stamp, convert_time(time_now))
        # if str(last_time_stamp) == convert_time(time_now):
        #    print("time did not change, update not called")
        #    return
        print("calling update")
        # update(convert_time(time_now), float(y))
        doc.add_next_tick_callback(partial(update, x=convert_time(time_now), y=float(y)))

    def start_monitor():
        global example
        global stop_signal
        print("Monitor started")
        mykeyword.callback(callback)
        mykeyword.monitor()
        while True:
            print(example)
            print("Thread is running")
            if stop_signal:
                print("stopping monitoring")
                mykeyword.monitor(start=False)
                stop_signal = False
                break
            time.sleep(10)

    renderer = hv.renderer('bokeh')
    hvplot = renderer.get_plot(curve_dmap).state
    doc.add_root(hvplot)
    # doc = renderer.server_doc(curve_dmap)
    # start_monitor()
    thread = Thread(name='Keyword_monitor', target=start_monitor)
    thread.start()
    #thread.join()

    # html = file_html(hvplot, CDN, "Plot: %s from %s" % (keyword, server))
    # return html


@app.route('/teststream/<server>/<keyword>', methods=['GET'])
def bkapp_page(server, keyword):
    global stream_server
    global stream_keyword
    stream_server = server
    stream_keyword = keyword
    remote_address = request.remote_addr
    remote_url = request.host_url
    host_name = remote_url.split('//')[1].split(':')[0]
    print("Starting a bokeh server on server %s/%s" % (host_name, remote_address))
    script = server_document('http://%s:5006/bkapp' % (host_name))
    print(script)
    print("Rendering template")
    return render_template("embed.html", script=script, template="Flask")

def bk_worker():
    # Can't pass num_procs > 1 in this configuration. If you need to run multiple
    # processes, see e.g. flask_gunicorn_embed.py
    server = Server({'/bkapp': keyword_stream}, io_loop=IOLoop(), allow_websocket_origin=['localhost:5002','kcwiserver:5002'])
    server.start()
    server.io_loop.start()

@app.route('/')
def index():
    return("Hello, welcome!")


if __name__ == "__main__":
    bokeh = Thread(name='bokeh_thread', target=bk_worker, daemon=True)
    bokeh.start()
    #bokeh.join()

    app.run(host='0.0.0.0',port=5002, debug=False)
