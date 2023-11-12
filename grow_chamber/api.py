import json
import datetime as dt
from flask import Flask, jsonify, request
from peewee import *
from playhouse.shortcuts import model_to_dict, dict_to_model

from db import *

app = Flask(__name__)


@app.before_request
def before_request():
    db.connect()


@app.after_request
def after_request(response):
    db.close()
    return response


@app.route("/")
def index():
    return "Mushroom Control"


@app.route("/logs")
def get_logs():
    log = Log.select().order_by(Log.timestamp.desc())
    return jsonify({"rows": [model_to_dict(l) for l in log]})


@app.route("/controls")
def get_controls():
    control = Control.select().order_by(Control.timestamp.desc())
    return jsonify({"rows": [model_to_dict(l) for l in control]})


@app.route("/controls", methods=["POST"])
def add_control():
    json = request.get_json()
    json["timestamp"] = dt.datetime.now()
    # TODO: add the timestamp here rather than from the request
    new_control = dict_to_model(Control, json, ignore_unknown=True)
    new_control.save()
    return "", 204
