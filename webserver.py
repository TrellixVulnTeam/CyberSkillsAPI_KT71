#!/usr/bin/python3
from flask import Flask, Response

import json
import os

app = Flask(__name__)

def listAllowedDates():
    allowedDates = []
    for fileName in os.listdir("./events"):
        year = fileName.split(";")[0]
        month = fileName.split(";")[1].split(".")[0]
        allowedDates.append({ "year" : year, "month" : month })
    return allowedDates

@app.route("/allowedDates")
def showAllowedDates():
    return Response(json.dumps(listAllowedDates()), mimetype="application/json")

@app.route("/<string:year>/<string:month>/")
def sendEventsJSON(year, month):
    if { "year" : year, "month" : month } in listAllowedDates():
        with open(f"./events/{year};{month}.json") as eventFile:
            return Response(json.dumps(json.load(eventFile)), mimetype="application/json")
    else:
        return "Didn't recognize either year or month", 422

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
