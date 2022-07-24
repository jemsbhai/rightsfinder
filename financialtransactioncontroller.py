from flask import Flask, request, abort, Response
from flask import redirect
from twilio.twiml.messaging_response import MessagingResponse
from flask_cors import CORS
from flask import render_template
import json
import sharesteadySmartContract as shalgo
import pymongo

from hashlib import sha256


aclient = shalgo.init_algo()
orgpri, orgpub = shalgo.get_account("tenant jump damage potato able prosper")
eventpri, eventpub = shalgo.get_account("e rural diary lecture mansion above ginger")

rate = 1000 ##price of basic, kwh per microAlgos

def initdb():
    
    mongostr = "mongodb+srv://teamzero:blah@cluster0.wa1hp.mongodb.net/test?retryWrites=true&w=majority"
    client = pymongo.MongoClient(mongostr)
    db = client["rightsfinder"]

    return client, db

app = Flask(__name__)
CORS(app)


@app.route("/")
def index():
    return render_template("MNMT.html")

@app.route("/about")
def about():
    return """
    <h1 style='color: red;'>I'm a red H1 heading!</h1>
    <p>This is a lovely little paragraph</p>
    <code>Flask is <em>awesome</em></code>"""



@app.route("/processregistration", methods=['GET', 'POST'])
def paybill():
    
    global aclient, orgpub, eventpub, eventpri, rate
    
    totalval = 0
    client, db = initdb()
    uvals = []
    
    col = db.regs
    
    for x in col.find():
        totalval += x['dep'] *rate
        uv = {}
        uv['userid'] = x['userid']
        uv['val'] = x['dep'] * rate
        uvals.append (uv)
        
        ##update dep
        col.update_one({"regid":x['regid']}, {"$set": {"dep":0}})
        rate = rate /2  ##progressive

    rate = 1000  ##reset
    
    totalval = int(totalval)
    ##payout
    print (totalval)
    gen, gh, first_valid_round, last_valid_round, fee = shalgo.init2(aclient)
    
    stx = shalgo.sendAmount(eventpub, fee, first_valid_round, last_valid_round, gh, orgpub, totalval, eventpri)
    shalgo.confirmTransaction(aclient, stx)
    
    print("registration paid and processed")
    
    ##now refund everyone
    
    col = db.users
    
    for x in col.find():
        # dep = x['deposit']
        ref = 0
        for y in uvals:
            if y['userid'] == x['id']:
                ref = x['staked'] - y['val']
                upub = x['public']
                ref = int(ref)
                
                stx =  shalgo.sendAmount(eventpub, fee, first_valid_round, last_valid_round, gh, upub, ref, eventpri)
                shalgo.confirmTransaction(aclient, stx)
                
                print ("refund for "+x['name'] + " paid")
                
                col.update_one({"userid":y['userid']}, {"$set": {"staked":0}})
                
            
    

    res = request.get_json()
    print (res)

    resraw = request.get_data()
    print (resraw)

##    args = request.args
##    form = request.form
##    values = request.values

##    print (args)
##    print (form)
##    print (values)

##    sres = request.form.to_dict()


    status = {}
    status["server"] = "up"
    status["request"] = res
    status["paidamount"] = totalval

    statusjson = json.dumps(status)

    print(statusjson)

    js = "<html> <body>OK THIS WoRKS</body></html>"

    resp = Response(statusjson, status=200, mimetype='application/json')
    ##resp.headers['Link'] = 'http://google.com'

    return resp




@app.route("/stakeandregister", methods=['POST'])
def makedepositl():
    
    res = request.get_json()
    print (res)

    resraw = request.get_data()
    print (resraw)
    
    global aclient, eventpub, rate
    
    totalval = 0
    client, db = initdb()
    uvals = []
    
    col = db.users
    
    for x in col.find():
        if x['id'] == res['userid']:
##            upub1 = x['public']
            amt = int(res['amount'])
            mne  = x['mnemonic']
            print (mne)
            upri, upub = shalgo.get_account(mne)
            
            print (upub)
##            if upub != upub1:
##                print ("errorred")
##                break
            
            gen, gh, first_valid_round, last_valid_round, fee = shalgo.init2(aclient)
    
            stx = shalgo.sendAmount(upub, fee, first_valid_round, last_valid_round, gh, eventpub, amt, upri)
            shalgo.confirmTransaction(aclient, stx)
            print("deposit made")
            
            odep = x['staked']
            ndep = odep + amt
                           
            col.update_one({"id":x['id']}, {"$set": {"staked":ndep}})
            break
                
            

##    args = request.args
##    form = request.form
##    values = request.values

##    print (args)
##    print (form)
##    print (values)

##    sres = request.form.to_dict()


    status = {}
    status["server"] = "up"
    status["request"] = res 

    statusjson = json.dumps(status)

    print(statusjson)

    js = "<html> <body>OK THIS WoRKS</body></html>"

    resp = Response(statusjson, status=200, mimetype='application/json')
    ##resp.headers['Link'] = 'http://google.com'

    return resp






@app.route("/dummyJson", methods=['GET', 'POST'])
def dummyJson():

    res = request.get_json()
    print (res)

    resraw = request.get_data()
    print (resraw)

##    args = request.args
##    form = request.form
##    values = request.values

##    print (args)
##    print (form)
##    print (values)

##    sres = request.form.to_dict()


    status = {}
    status["server"] = "up"
    status["request"] = res 

    statusjson = json.dumps(status)

    print(statusjson)

    js = "<html> <body>OK THIS WoRKS</body></html>"

    resp = Response(statusjson, status=200, mimetype='application/json')
    ##resp.headers['Link'] = 'http://google.com'

    return resp


if __name__ == '__main__':
    # app.run()
    # app.run(debug=True, host = '45.79.199.42', port = 8090)
    app.run(debug=True, host = 'localhost', port = 8090)  ##change hostname here
