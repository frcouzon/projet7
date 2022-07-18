from flask import Flask, request, render_template, session, jsonify
import pickle

app = Flask(__name__)

@app.route('/api/getprediction/', methods=['get'])
def getprediction():
    clientid=request.args['clientid']
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
    return jsonify(dictionnaire)

if __name__ == "__main__":
    app.run(debug=True)