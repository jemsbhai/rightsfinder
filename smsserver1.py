from flask import Flask, request, redirect, Response
from twilio.twiml.messaging_response import MessagingResponse
# import tns
# import dataloader
from twilio.rest import Client 
import requests
import json
# import pymongo
import time
from flask_cors import CORS






incomingstate = 0
incomingnum = ""
doctorname = "Dr Victor Von Doom"
patientname = "Reed Richards"
aptdate = "02/01/2022"
apttime = "16:20"


qid = "-1"
userid = "-1"
onum = 0

oitems = ""



def sendwhatsapp(text, tonum, fromnum):
    
    account_sid = 'xxxxxxxxxxxxxxxxxxx' 
    auth_token = 'xxxxxxxxxxxxxxxxxxxxx' 
    client = Client(account_sid, auth_token) 
    
    message = client.messages.create( 
                                # from_='whatsapp:+14155238886',  
                                from_=fromnum,
                                # body='Your Twilio code is 1238432',
                                # body='Your story is somewhat funny. Details: http://www.aphroditesaves.tech/',  
                                # body='Your appointment is coming up on July 21 at 3PM',    
                                body=text,
                                # to='whatsapp:+13218775974' 
                                to=tonum
                            ) 
    
    print(message.sid)

def getinfo(statename):
    
    statename = statename.capitalize()
    
    print(statename)
    url = "https://us-central1-aiot-fit-xlab.cloudfunctions.net/rightsfinder"

    payload = json.dumps({
    "action": "checklegalstatus",
    "state": statename
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    
    js = json.loads(response.text)
    
    return js




def getuserfromphone(phone):
    
    global userid

    url = "https://us-central1-aiot-fit-xlab.cloudfunctions.net/rightsfinder"

    payload = json.dumps({
    "action": "getuseridfromphone",
    "phone": phone
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    
    js = json.loads(response.text)
    
    if js['status'] == "found":
        name = js['name']
        points = js['balance']
        userid = js['id']
        
        return name, points

    
    userid = "-1"
    
    return "unknown", -1





app = Flask(__name__)
CORS(app)

def setcreds(nc):
    global cred
    cred = nc

    return "success"

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/smsbase", methods=['POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""

    global incomingstate, incomingnum,  userid
    global cred
    global oitems
    global onum
    global texturl
    # global doctorname, patientname, aptdate, apttime
    
    # client, db = initdb()
    
    print(request.values['From'])
    
    incomingnum = request.values['From']
    
    incomingnum2 = incomingnum.replace('+', '')
    
    print (incomingnum)
    
    # n, p = getuserfromphone(incomingnum)
    n = "friend"
    p = 1
    

    incoming = request.values['Body']
    
    incoming = incoming.lower()

    print("incoming text is " + incoming)


    # Start our TwiML response
    resp = MessagingResponse()

    flag = 0
    outstring = "Unfortunately Rightsfinder did not understand the following message ..." + incoming
    
    
    if "is abortion legal in" in incoming:
        
        statename = incoming.replace("is abortion legal in ", "")
        statename = statename.replace("?", "")
        
        info = getinfo(statename)
        
        print(info)

        if info['status'] != "found":
            outstring= "Sorry, Rightsfinder could not find information about! " + statename +  " please try again with a state name (spelling sensitive) "
            resp.message(outstring)
            return str(resp)
 
        outstring= "The current legal status of abortion in  " + statename +  " is " + info['legal status'] + " and this is in effect " + info['time of effect'] + "; Details: " + info['details'] + ". thank you for using Rightsfinder"
        resp.message(outstring)
        
        return str(resp)


    if "how can i get funding" in incoming:
        
 
        outstring= "Please use the Rightsfinder App to register a free account and submit a donation request. We will connect you to various organizations and private donors to fulfil your request. thank you for using Rightsfinder"
        resp.message(outstring)
        
        return str(resp)


    # Add a message
    if flag ==0:
        outstring = "Unfortunately Rightsfinder did not understand your message. Please message me again "
    
    resp.message(outstring)

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True, host = 'localhost', port = 8004)
    # app.run(debug=True, host = '45.79.199.42', port = 8004)
