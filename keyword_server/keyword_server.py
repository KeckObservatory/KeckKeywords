from flask import Flask, json, jsonify, request, render_template
import subprocess
import sys
import os
import warnings
from datetime import datetime
import time
from math import pi
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
    from threading import Thread
    from functools import partial
    from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature


except ImportError as error:
    use_graphics = False
    warnings.warn("One of the graphics modules is not available. Graphics functions are disabled.")
    print(error)

app = Flask(__name__)


def json_load(data):
    return json.loads(data)


def json_dump(data):
    return json.dumps(data)


def json_pretty(data):
    return json.dumps(data, sort_keys=True, indent=4)


@app.route('/show/<server>/<keyword>')
def show_keyword(server,keyword):
    mykeyword = ktl.cache(server,keyword)
    value = mykeyword.read()
    return json_dump(value)


@app.route('/modify/<server>/<keyword>', methods=['POST','PUT'])
def modify_keyword(server,keyword):
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


@app.route('/plot/<server>/<keyword>')
def plot_keyword(server,keyword):
    useBokeh = True
    useHV = False
    if use_graphics is False:
        return json_dump("The graphics system is disabled")
    hv.extension('bokeh')
    cmd = "gshow -s %s %s -terse -date '1 day ago'" % (server,keyword)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    output = output.decode().splitlines()
    #print(output)
    p_status = p.wait()
    mykeyword = ktl.cache(server, keyword)
    mykeyword.monitor()
    units = mykeyword['units']

    mydata = pd.DataFrame(columns=['time','value'])
    for line in output:
        #print(str(line))
        if "#" in line:
            continue
        mydata = mydata.append({
            'time': datetime.strptime(line.split()[0], "%Y-%m-%dT%H:%M:%S.%f"),
            'value': float(line.split()[1])
             }, ignore_index=True)

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

def modify_doc(doc):
    df = sea_surface_temperature.copy()
    source = ColumnDataSource(data=df)

    plot = figure(x_axis_type='datetime', y_range=(0, 25), y_axis_label='Temperature (Celsius)',
                  title="Sea Surface Temperature at 43.18, -70.43")
    plot.line('time', 'temperature', source=source)

    def callback(attr, old, new):
        if new == 0:
            data = df
        else:
            data = df.rolling('{0}D'.format(new)).mean()
        source.data = ColumnDataSource(data=data).data

    slider = Slider(start=0, end=30, value=0, step=1, title="Smoothing by N Days")
    slider.on_change('value', callback)

    doc.add_root(column(slider, plot))

    doc.theme = Theme(filename="theme.yaml")


#@app.route('/stream')
def keyword_stream(doc):
    keyword = 'temperature'
    server = 'kt1s'
    tmp1 = ktl.cache('kt1s', 'tmp1')
    mykeyword = tmp1

    def convert_time(timestamp):
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    initial_y = mykeyword.read(binary=True)
    global example
    example = pd.DataFrame(
        {'x': [convert_time(time.time())],
         'y': [initial_y]},
        columns=['x', 'y'])
    dfstream = Buffer(example, length=100, index=False)
    curve_dmap = hv.DynamicMap(hv.Points, streams=[dfstream]).options(color='red', line_width=5, width=800, height=500, xrotation=90)

    #doc = curdoc()

    @gen.coroutine
    def update(x, y):
        print("Update called")
        global example
        example = example.append({'x': x, 'y': y}, ignore_index=True)
        #html = file_html(hvplot, CDN, "Plot: %s from %s" % (keyword, server))
        #return html

        dfstream.send(example)
        print(example.head())

    def callback(keyword):
        print("call back called")
        y = keyword.binary
        print("y:" + str(y))
        time_now = keyword.timestamp
        print("timestamp:" + str(time_now))
        last_time_stamp = example.iloc[-1]['x']
        print(last_time_stamp)
        if last_time_stamp == convert_time(time_now):
            print("time did not change, update not called")
            return
        print("calling update")
        #update(convert_time(time_now), float(y))
        doc.add_next_tick_callback(partial(update,  x=convert_time(time_now), y=float(y)))

    def start_monitor():
        global example
        print("Monitor started")
        mykeyword.callback(callback)
        mykeyword.monitor()
        while True:
            print(example)
            print("Thread is running")
            time.sleep(10)

    renderer = hv.renderer('bokeh')
    hvplot = renderer.get_plot(curve_dmap).state
    doc.add_root(hvplot)
    #doc = renderer.server_doc(curve_dmap)
    #start_monitor()
    thread = Thread(target=start_monitor)
    thread.start()

    #html = file_html(hvplot, CDN, "Plot: %s from %s" % (keyword, server))
    #return html



    
@app.route('/teststream', methods=['GET'])
def bkapp_page():
    print("Connecting to bokeh server for display")
    script = server_document('http://localhost:5006/bkapp')
    return render_template("embed.html", script=script, template="Flask")

def bk_worker():
    # Can't pass num_procs > 1 in this configuration. If you need to run multiple
    # processes, see e.g. flask_gunicorn_embed.py
    server = Server({'/bkapp': keyword_stream}, io_loop=IOLoop(), allow_websocket_origin=["*"])
    server.start()
    server.io_loop.start()

@app.route('/')
def index():
    return("Hello, welcome!")

    
from threading import Thread
Thread(target=bk_worker).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5002, debug=False)
