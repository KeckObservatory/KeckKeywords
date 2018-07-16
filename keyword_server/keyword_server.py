from flask import Flask, json, jsonify, request
import subprocess
import sys
import os
import warnings
from datetime import datetime
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
    sys.exit(1)
use_graphics = True
try:
    import pandas as pd
    import holoviews as hv
    from holoviews.streams import Buffer
    from bokeh.embed import file_html
    from bokeh.resources import CDN
    from bokeh.plotting import curdoc
    from tornado import gen
    from threading import Thread
    from functools import partial

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
    if use_graphics is False:
        return json_dump("The graphics system is disabled")
    hv.extension('bokeh')
    cmd = "gshow -s %s %s -terse -date '1 day ago'" % (server,keyword)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output,err) = p.communicate()
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
    #source = ColumnDataSource(mydata)
    #print(source)
    #print(mydata.head())
    #p = figure(x_axis_type='datetime')
    #p.circle(x='time', y='value',source=source)
    #p.xaxis.major_label_orientation = pi/4
    #p.xaxis.formatter=DatetimeTickFormatter(
    #    hours=["%d %B %Y"],
    #    days=["%d %B %Y"],
    #    months=["%d %B %Y"],
    #    years=["%d %B %Y"],
    #)
    #html = file_html(p, CDN, "my plot")
    #return html

    # pyviz solution generating pure html
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
    return html

@app.route('/stream')
def keyword_stream():
    keyword = 'pressure'
    server = 'kbvs'
    pressure = ktl.cache('kt1s', 'tmp1')
    mykeyword = exptime

    def convert_time(timestamp):
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    initial_y = mykeyword.read(binary=True)
    example = pd.DataFrame({'x': [convert_time(time.time())], 'y': [initial_y]}, columns=['x', 'y'])

    dfstream = Buffer(example, length=100, index=False)

    @gen.coroutine
    def update(x, y):
        global example
        if y < 0.1:
            example = pd.DataFrame({'x': x, 'y': 0}, columns=['x', 'y'])
        else:
            example = example.append({'x': x, 'y': y}, ignore_index=True)
        dfstream.send(example)
        print(example.head())


    pressure = ktl.cache('kt1s', 'tmp1')
    exptime = ktl.cache('kbds', 'elaptime')
    ttime = ktl.cache('kbds', 'ttime')
    mykeyword = exptime

    def convert_time(timestamp):
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    initial_y = mykeyword.read(binary=True)
    example = pd.DataFrame({'x': [convert_time(time.time())], 'y': [initial_y]}, columns=['x', 'y'])

    dfstream = Buffer(example, length=100, index=False)

    doc = curdoc()

    curve_dmap = hv.DynamicMap(hv.Points, streams=[dfstream]).options(color='red', line_width=5, width=1200,
                                                                      xrotation=90)
    example = pd.DataFrame({'x': x, 'y': 0}, columns=['x', 'y'])
    @gen.coroutine
    def update(x, y):
        global example
        example = example.append({'x': x, 'y': y}, ignore_index=True)
        dfstream.send(example)
        print(example.head())

    def callback(keyword):
        global example
        y = mykeyword.binary
        time_now = mykeyword.timestamp
        last_time_stamp = example.iloc[-1]['x']
        print(last_time_stamp)
        if last_time_stamp == convert_time(time_now):
            return
        doc.add_next_tick_callback(partial(update, x=convert_time(time_now), y=float(y)))

    def start_monitor():
        mykeyword.callback(callback)
        mykeyword.monitor()
        while True:
            pass

    #doc = hv.renderer('bokeh').server_doc(curve_dmap)
    renderer = hv.renderer('bokeh')
    hvplot = renderer.get_plot(myplot).state

    thread = Thread(target=start_monitor)
    thread.start()

    html = file_html(hvplot, CDN, "Plot: %s from %s" % (keyword, server))
    return html




@app.route('/')
def index():
    return("Hello, welcome!")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002, debug=True)
