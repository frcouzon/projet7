from dataclasses import dataclass
from distutils.cmd import Command
from inspect import modulesbyfile
from multiprocessing.spawn import import_main_path
from flask import Flask, request, render_template, session
import pickle
import numpy as np
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput
from bokeh.io import curdoc
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.plotting import figure, output_file, show
from bokeh.resources import INLINE
from bokeh.models.sources import AjaxDataSource
from matplotlib import pyplot as plt
from matplotlib import cm
from plotly import graph_objects as go 
import json
import plotly

app = Flask(__name__)
app.secret_key = "abc"  

mydata = pickle.load(open('dfImputeID.pkl', 'rb'))
myregression = pickle.load(open('model.pkl', 'rb'))
@app.route('/')
def index():
    return render_template('test.html')

@app.route('/getprediction',methods=['POST'])
def getprediction(): 
    clientid = request.form['clientid']
    if 'idclient' in session:
        session.pop('idclient', None)
    session.pop('idclient', None)
    session["idclient"]=clientid
    if int(clientid) in mydata["ID"].values:
        clientinfo=mydata[mydata["ID"]==int(clientid)]
        clientinfo = clientinfo.drop(['ID'], axis=1)
        clientinfo = clientinfo.drop(['TARGET'], axis=1)
        valpred=myregression.predict_proba(clientinfo)

        x = np.arange(2, 50, step=.5)
        y = np.sqrt(x) + np.random.randint(2,50)
        plot = figure(plot_width=400, plot_height=400,title=None, toolbar_location="below")
        plot.line(x,y)

        script, div = components(plot)
        kwargs = {'script': script, 'div': div}
        kwargs['title'] = 'bokeh-with-flask' 
        #val1=str(round(clientinfo["EXT_SOURCE_1"].values[0],3))
        #val2=str(round(clientinfo["EXT_SOURCE_2"].values[0],3))
        #val3=str(round(clientinfo["EXT_SOURCE_3"].values[0],3))
        #val4=str(round(clientinfo["DAYS_EMPLOYED_PERC"].values[0],3))

        #moy1=str(round(mydata["EXT_SOURCE_1"].mean(),3))
        #moy2=str(round(mydata["EXT_SOURCE_2"].mean(),3))
        #moy3=str(round(mydata["EXT_SOURCE_3"].mean(),3))
        #moy4=str(round(mydata["DAYS_EMPLOYED_PERC"].mean(),3))
        #kwargs={'val1':val1, 'val2':val2,'val3':val3,'val4':val4,'moy1':moy1,'moy2':moy2,'moy3':moy3,'moy4':moy4}
        kwargs=getinfoclient(clientinfo, mydata)

        valgauge = float(valpred[:,1])
        valgauge=valgauge*100
        valgauge=valgauge/2
        valgauge=int(valgauge)     
        graphJSON = json.dumps(getgauge(valgauge), cls=plotly.utils.PlotlyJSONEncoder)
        c=float(valpred[:,1])
        if (c>0.8):
            return render_template('result.html', client=clientid,graphJSON=graphJSON, output='Le client est autorisé au crédit sans risque:{}'.format(str(c)), **kwargs)
        elif (c>0.6):
            return render_template('result.html', client=clientid,graphJSON=graphJSON, output='Le client est autorisé au crédit avec un risque moindre :{}'.format(c), **kwargs)
        elif (c>0.4):
             return render_template('result.html', client=clientid,graphJSON=graphJSON, output='Le client n est pas autorisé au crédit risque élevé :{}'.format(c), **kwargs)        
        else:
             return render_template('result.html', client=clientid, graphJSON=graphJSON, output='Le client n est pas autorisé au crédit risque tres élevé :{}'.format(c), **kwargs)
    else:
        return render_template('result.html',output='Le client {} est inconnu'.format(clientid))
    #o=mydata["CODE_GENDER"][0]
    #if  clientid =="0":
    #    return render_template('test.html', output='Le client 00 est autorisé au crédit :') 
    #elif clientid=='1':
    #    return render_template('test.html', output='Le client 11 n est pas autorisé au crédit : {}'.format(myregression.get_params())) 
    #else:
    #    return render_template('test.html',output='Le client {} est inconnu'.format(clientid))

@app.route('/getexplication',methods=['POST','GET'])
def getexplication():    
    select = request.form.get('col_group_name')
    curdoc().clear()
    clientid=session["idclient"]
    print('Le client : {}'.format(str(clientid)))
    data=mydata[select]
    cols = ['red','red','red','red', 'red','red','red','red','red', 'red']
    hist, edges = np.histogram(data, density=True, bins=10)
    intclient=int(clientid)
    clientvalue=mydata[mydata["ID"]==intclient][select]
    i=0
    while (clientvalue.values[0]>edges[i]):
        i=i+1
    cols[i-1]='navy'
    p=figure()
    p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], line_color="white",color=cols)

    script, div = components(p)
    kwargs = {'script': script, 'div': div}
    kwargs['title'] = 'bokeh-with-flask' 
    plot = figure(plot_width=400, plot_height=400,title=None, toolbar_location="below")
    x = np.arange(2, 50, step=.5)
    y = np.sqrt(x) + np.random.randint(2,50)
    plot.line(x,y)
    otherscript, otherdiv = components(plot)
    otherkwargs = {'script': otherscript, 'div': otherdiv}
    otherkwargs['title'] = 'bokeh-with-flask' 
    clientinfo=mydata[mydata["ID"]==int(clientid)]
    otherkwargs=getinfoclient(clientinfo, mydata)

    return render_template('result.html', client=clientid, output2='Le client est autorisé au crédit sans risque:{}'.format(str(select)), **kwargs, **otherkwargs)

@app.route('/getdictionnary',methods=['POST','GET'])
def getdictionnary():
    clientid=session["idclient"]
    mydata = pickle.load(open('static/data/dfImputeID.pkl', 'rb'))
    myregression = pickle.load(open('static/data/model.pkl', 'rb'))
    clientinfo=mydata[mydata["ID"]==int(clientid)]
    clientinfo = clientinfo.drop(['ID'], axis=1)
    clientinfo = clientinfo.drop(['TARGET'], axis=1)
    valpred=myregression.predict_proba(clientinfo)
    c=float(valpred[:,1])
    dictionnaire = {
        'valpred': c
    }
    return render_template('tesstapi.html', val=dictionnaire["valpred"])



@app.route('/getchart',methods=['POST','GET'])
def getchart(): 
    curdoc().clear()
  
    source = AjaxDataSource(data=dict(x=[], y1=[], y2=[], y3=[]), data_url='http://127.0.0.1:5050/data', polling_interval=1000)

    x = np.arange(2, 50, step=.5)
    y = np.sqrt(x) + np.random.randint(2,50)
    plot = figure(plot_width=400, plot_height=400,title=None, toolbar_location="below")
    plot.line(x,y)

    data = np.random.normal(0, 0.5, 1000)
    cols = ['red','green','orange','navy', 'cyan','red','green','orange','navy', 'cyan']
    hist, edges = np.histogram(data, density=True, bins=10)
    p=figure()
    p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], line_color="white",color=cols)



    script, div = components(p)
    kwargs = {'script': script, 'div': div}
    kwargs['title'] = 'bokeh-with-flask' 


    return render_template("test_stackoverflow.html", **kwargs)


def getinfoclient(dataclient, globaldata):
    val1=str(round(dataclient["EXT_SOURCE_1"].values[0],3))
    val2=str(round(dataclient["EXT_SOURCE_2"].values[0],3))
    val3=str(round(dataclient["EXT_SOURCE_3"].values[0],3))
    val4=str(round(dataclient["DAYS_EMPLOYED_PERC"].values[0],3))

    moy1=str(round(globaldata["EXT_SOURCE_1"].mean(),3))
    moy2=str(round(globaldata["EXT_SOURCE_2"].mean(),3))
    moy3=str(round(globaldata["EXT_SOURCE_3"].mean(),3))
    moy4=str(round(globaldata["DAYS_EMPLOYED_PERC"].mean(),3))
    return {'val1':val1, 'val2':val2,'val3':val3,'val4':val4,'moy1':moy1,'moy2':moy2,'moy3':moy3,'moy4':moy4}


def getgauge(val_pct):
    plot_bgcolor = "#def"
    quadrant_colors = [plot_bgcolor, "#f25829", "#f25829",  "#f2a529", "#eff229", "#2bad4e", ] 
    quadrant_text = [ "", "<b>PAS DE CREDIT</b>","", "<b>GROS RISQUE</b>", "<b>FAIBLE RISQUE</b>", "<b>SANS RISQUE</b>"]
    n_quadrants = len(quadrant_colors) - 1

    current_value = val_pct
    min_value = 0
    max_value = 50
    hand_length = np.sqrt(2) / 4
    hand_angle = np.pi * (1 - (max(min_value, min(max_value, current_value)) - min_value) / (max_value - min_value))

    fig = go.Figure(
        data=[
            go.Pie(
                values=[0.5] + (np.ones(n_quadrants) / 2 / n_quadrants).tolist(),
                rotation=90,
                hole=0.5,
                marker_colors=quadrant_colors,
                text=quadrant_text,
                textinfo="text",
                hoverinfo="skip",
            ),
        ],
        layout=go.Layout(
            showlegend=False,
            margin=dict(b=0,t=10,l=10,r=10),
            width=450,
            height=450,
            paper_bgcolor=plot_bgcolor,
            annotations=[
                go.layout.Annotation(
                    text=f"<b>RISQUE CREDIT</b>",
                    x=0.5, xanchor="center", xref="paper",
                    y=0.25, yanchor="bottom", yref="paper",
                    showarrow=False,
                )
            ],
            shapes=[
                go.layout.Shape(
                    type="circle",
                    x0=0.48, x1=0.52,
                    y0=0.48, y1=0.52,
                    fillcolor="#333",
                    line_color="#333",
                ),
                go.layout.Shape(
                    type="line",
                    x0=0.5, x1=0.5 + hand_length * np.cos(hand_angle),
                    y0=0.5, y1=0.5 + hand_length * np.sin(hand_angle),
                    line=dict(color="#333", width=4)
                )
            ]
        )
    )
    fig.update_layout(
    autosize=False,
    width=450,
    height=250,
    margin=dict(
        l=0,
        r=0,
        b=0,
        t=0,
        pad=4
    )
    )
    return fig