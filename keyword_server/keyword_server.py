from flask import Flask, json, render_template, Response, jsonify, request
import subprocess
import sys
sys.path.append('/kroot/rel/default/lib/python')
import ktl
import numpy as np
from math import pi
import pandas as pd
#from io import StringIO
import holoviews as hv
#import holoviews.plotting.mpl
from bokeh.embed import components, file_html
#from bokeh.document import Document
#from bokeh.plotting import figure
#from bokeh.resources import CDN
#from bokeh.models import ColumnDataSource, DatetimeTickFormatter
import pprint
from datetime import datetime

hv.extension('bokeh')

#import json_util

app = Flask(__name__)

def json_load(data):
    return json.loads(data) #, object_hook=json_util.object_hook)

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
    #print("Content:" + content)
    print("Request data: %s" % (str(content)))
    mykeyword.write(content['value'])
    new_value = mykeyword.read()
    return json_dump(new_value)

@app.route('/showkeywords/<server>')
def show_keywords(server):
    cmd = 'show keywords -s %s' % (server)
    p = subprocess.Popen(cmd, stdout = subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    output = output.decode().splitlines()
    return jsonify(output)


@app.route('/plot/<server>/<keyword>')
def plot_keyword(server,keyword):
    cmd = "gshow -s %s %s -terse -date '1 day ago'" % (server,keyword)
    p = subprocess.Popen(cmd, stdout = subprocess.PIPE, shell=True)
    (output,err) = p.communicate()
    output = output.decode().splitlines()
    print(output)
    p_status = p.wait()
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
    renderer  = hv.renderer('bokeh')
    myplot = hv.Points(mydata).options(width=800, height=500,xrotation=90, size=5)
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


@app.route('/')
def index():
    return("Hello, welcome!")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002, debug=True)
