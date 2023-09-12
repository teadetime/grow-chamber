from flask import Flask, jsonify, request
import sqlite3

from constants import (
    DB_CTL_TBL,
    DB_LOG_TBL,
    DBNAME,
    DEFAULT_AIR_PRD,
    DEFAULT_HUMIDITY,
    DEFAULT_AIR_DURATION,
    DEFAULT_HUMIDITY_LOW,
    DEFAULT_HUMIDITY_HIGH,
)

app = Flask(__name__)


@app.route("/")
def index():
    return "Hello world"


incomes = [{"description": "salary", "amount": 5000}]


@app.route("/logs")
def get_logs():
    con = sqlite3.connect(DBNAME, check_same_thread=False)
    cur = con.cursor()
    logs = cur.execute(
        f"SELECT * FROM {DB_LOG_TBL} ORDER BY timestamp DESC LIMIT 100"
    ).fetchall()
    cur.close()
    con.close()
    return jsonify(logs)


@app.route("/controls")
def get_controls():
    con = sqlite3.connect(DBNAME, check_same_thread=False)
    cur = con.cursor()
    logs = cur.execute(
        f"SELECT * FROM {DB_CTL_TBL} ORDER BY timestamp DESC LIMIT 100"
    ).fetchall()
    cur.close()
    con.close()
    return jsonify(logs)


@app.route("/controls", methods=["POST"])
def add_income():
    json = request.get_json()
    humidity = json["humidity"]
    fan_period = json["fan_period"]
    fan_duration = json["fan_duration"]
    print(json.items())
    con = sqlite3.connect(DBNAME, check_same_thread=False)
    cur = con.cursor()
    cur.execute(
        f"INSERT INTO {DB_CTL_TBL} VALUES \
            ('{dt.datetime.now()}', {humidity}, \
            {fan_period}, {fan_duration});"
    )
    con.commit()
    cur.close()
    con.close()
    return "", 204
