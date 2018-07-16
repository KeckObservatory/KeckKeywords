
import holoviews as hv
hv.extension('bokeh')
import pandas as pd
import ktl
import time
from holoviews.streams import Buffer
import datetime
from bokeh.plotting import curdoc
import time
from tornado.ioloop import IOLoop
from tornado import gen
from threading import Thread
from functools import partial

pressure = ktl.cache('kt1s','tmp1')
exptime = ktl.cache('kbds','elaptime')
ttime = ktl.cache('kbds','ttime')
mykeyword = exptime
def convert_time(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

initial_y = mykeyword.read(binary=True)
example = pd.DataFrame({'x':[convert_time(time.time())],'y':[initial_y]}, columns=['x','y'])

dfstream = Buffer(example, length=100, index=False)

doc=curdoc()

curve_dmap = hv.DynamicMap(hv.Points, streams=[dfstream]).options(color='red',line_width=5,width=1200, xrotation=90)

@gen.coroutine
def update(x,y):
    global example
    if y<0.1:
        example = pd.DataFrame({'x':x, 'y':0}, columns=['x','y'])
    else:
        example = example.append({'x':x, 'y':y}, ignore_index=True)
    dfstream.send(example)
    print(example.head())    

def callback(keyword):
    global example
    y = mykeyword.binary
    time_now= mykeyword.timestamp
    last_time_stamp = example.iloc[-1]['x']
    print(last_time_stamp)
    if last_time_stamp == convert_time(time_now):
        return
    doc.add_next_tick_callback(partial(update,x=convert_time(time_now), y=float(y)))

def start_monitor():
    mykeyword.callback(callback)
    mykeyword.monitor()
    while True:
        pass

doc = hv.renderer('bokeh').server_doc(curve_dmap)


thread = Thread(target=start_monitor)
thread.start()
