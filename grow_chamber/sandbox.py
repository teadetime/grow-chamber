import datetime as dt
import sqlite3
import threading
from time import sleep

from api import app
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

def db_setup() -> None:
    con = sqlite3.connect(DBNAME)
    cur = con.cursor()

    control_tbl = cur.execute(
        f"SELECT * FROM sqlite_master WHERE name ='{DB_CTL_TBL}' and type='table'"
    ).fetchone()
    log_tbl = cur.execute(
        f"SELECT * FROM sqlite_master WHERE name = '{DB_LOG_TBL}' and type='table'"
    ).fetchone()
    if control_tbl is None:
        cur.execute(
            f"CREATE TABLE IF NOT EXISTS {DB_CTL_TBL} \
         (timestamp TIMESTAMP PRIMARY KEY     NOT NULL,\
         humidity            REAL     NOT NULL,\
         fan_period            INT     NOT NULL,\
         fan_duration            INT     NOT NULL);"
        )
    if log_tbl is None:
        cur.execute(
            f"CREATE TABLE IF NOT EXISTS {DB_LOG_TBL} \
         (timestamp TIMESTAMP PRIMARY KEY     NOT NULL, \
         humidity            REAL     NOT NULL, \
         temp                 REAL     NOT NULL, \
         humidifier_status   INT     NOT NULL, \
         air_status            INT     NOT NULL);"
        )
    # Check that control has an entry
    control_pts = cur.execute(f"SELECT * FROM {DB_CTL_TBL}").fetchone()
    if control_pts is None:
        cur.execute(
            f"INSERT INTO {DB_CTL_TBL} VALUES \
            ('{dt.datetime.now()}', {DEFAULT_HUMIDITY}, \
            {DEFAULT_AIR_PRD}, {DEFAULT_AIR_DURATION});"
        )

    # Close and commit to the DB
    con.commit()
    cur.close()
    con.close()


class State:
    def __init__(self, humidity=40.0, temp=20.0) -> None:
        self.fan_on: bool = False
        self.humid_on: bool = False
        self.humidity: float = humidity
        self.temp: float = temp


def monitor() -> None:
    prev_fan_time = dt.datetime.now()
    state = State()
    con = sqlite3.connect(DBNAME, check_same_thread=False)
    cur = con.cursor()

    while True:
        # Read value from DB
        _time, humidity_stp, fan_prd, fan_dur = cur.execute(
            f"SELECT * FROM {DB_CTL_TBL} ORDER BY timestamp DESC LIMIT 1;"
        ).fetchone()
        print(
            f"Humidity_stp: {humidity_stp},\
             Fan_period_stp: {fan_prd}, Fan_duration: {fan_dur}"
        )
        # Take Action
        # Get Current readings via pi

        # Look to see if scheduled event (FAN) should turn on
        if not state.fan_on and (
            dt.datetime.now() - prev_fan_time
        ) > dt.timedelta(seconds=DEFAULT_AIR_PRD):
            print("Turning Fan on!")
            state.fan_on = True
        elif state.fan_on and (
            dt.datetime.now() - prev_fan_time
        ) > dt.timedelta(seconds=DEFAULT_AIR_DURATION):
            print("Turning Fan off")
            state.fan_on = False

        # Check to see if humidifier should turn off
        if state.humid_on:
            if state.humidity >= DEFAULT_HUMIDITY + DEFAULT_HUMIDITY_HIGH:
                state.humid_on = False
                print("Turning Humidifier Off!")
        # Check to see if humidifier should turn on
        else:
            if state.humidity <= DEFAULT_HUMIDITY - DEFAULT_HUMIDITY_LOW:
                state.humid_on = True
                print("Turning Humidifier On!")

        # Log the result
        cur.execute(
            f"INSERT INTO {DB_LOG_TBL} VALUES \
            ('{dt.datetime.now()}', {DEFAULT_HUMIDITY}, \
            {20.4}, {state.humid_on}, {state.fan_on});"
        )
        con.commit()
        sleep(3)

if __name__ == "__main__":
    db_setup()
    control_thread = threading.Thread(target=monitor, args=[])
    control_thread.start()
    app.run(debug=True, use_reloader=False, port=8000, host="0.0.0.0")
