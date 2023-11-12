from peewee import *
import datetime as dt
import threading
from time import sleep

from api import app

from db import *
from constants import (
    DEFAULT_AIR_PRD,
    DEFAULT_HUMIDITY,
    DEFAULT_AIR_DURATION,
    DEFAULT_HUMIDITY_LOW,
    DEFAULT_HUMIDITY_HIGH,
)


def monitor() -> None:
    prev_fan_time = dt.datetime.now()
    state = State()

    while True:
        # Read value from DB
        db.connect()
        control = Control.select().order_by(Control.timestamp.desc()).get()
        db.close()
        print(
            f"Humidity_stp: {control.humidity_setpoint},\
             Fan_period_stp: {control.fan_period}, Fan_duration: {control.fan_duration}"
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
        db.connect()
        log = Log(
            timestamp=dt.datetime.now(),
            humidity=DEFAULT_HUMIDITY,
            temperature=20.4,
            humidity_status=state.humid_on,
            fan_status=state.fan_on,
        )
        log.save()
        db.close()

        sleep(5)


if __name__ == "__main__":
    db_setup()
    control_thread = threading.Thread(target=monitor, args=[])
    control_thread.start()
    app.run(debug=True, use_reloader=False, port=8000, host="0.0.0.0")
