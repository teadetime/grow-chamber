from peewee import *
import datetime as dt
import threading
from time import sleep
import board
import adafruit_ahtx0
import RPi.GPIO as GPIO           # import RPi.GPIO module

from api import app

from db import *
from constants import (
    DEFAULT_AIR_PRD,
    DEFAULT_HUMIDITY,
    DEFAULT_AIR_DURATION,
    DEFAULT_HUMIDITY_LOW,
    DEFAULT_HUMIDITY_HIGH,
    HUMIDIFIER_PIN,
    FAN_PIN
)


def monitor() -> None:
    prev_fan_time = dt.datetime.now()
    state = State()
    i2c = board.I2C() 
    humidity_sensor = adafruit_ahtx0.AHTx0(i2c)


    GPIO.setmode(GPIO.BCM)            # choose BCM or BOARD
    GPIO.setup(HUMIDIFIER_PIN, GPIO.OUT) # set a port/pin as an output
    GPIO.setup(FAN_PIN, GPIO.OUT) # set a port/pin as an output

    GPIO.output(HUMIDIFIER_PIN, 0)       # set port/pin value to 1/GPIO.HIGH/True
    GPIO.output(FAN_PIN, 0)       # set port/pin value to 0/GPIO.LOW/False

    while True:
        # Read value from DB
        db.connect()
        control = Control.select().order_by(Control.timestamp.desc()).get()
        db.close()
        # Get Current readings via pi
        state.humidity = humidity_sensor.relative_humidity
        state.temp = humidity_sensor.temperature

        print(
            f"Humidity_stp: {control.humidity_setpoint} Current: {state.humidity},\
             Fan_period_stp: {control.fan_period}, Fan_duration: {control.fan_duration}"
        )

        # Look to see if scheduled event (FAN) should turn on
        if not state.fan_on and (
            dt.datetime.now() - prev_fan_time
        ) > dt.timedelta(seconds=DEFAULT_AIR_PRD):
            print("Turning Fan on!")
            state.fan_on = True
            GPIO.output(FAN_PIN, 1)
        elif state.fan_on and (
            dt.datetime.now() - prev_fan_time
        ) > dt.timedelta(seconds=DEFAULT_AIR_DURATION):
            print("Turning Fan off")
            state.fan_on = False
            GPIO.output(FAN_PIN, 0)

        # Check to see if humidifier should turn off
        if state.humid_on:
            if state.humidity >= DEFAULT_HUMIDITY + DEFAULT_HUMIDITY_HIGH:
                state.humid_on = False
                print("Turning Humidifier Off!")
                GPIO.output(HUMIDIFIER_PIN, 0)
        # Check to see if humidifier should turn on
        else:
            if state.humidity <= DEFAULT_HUMIDITY - DEFAULT_HUMIDITY_LOW:
                state.humid_on = True
                print("Turning Humidifier On!")
                GPIO.output(HUMIDIFIER_PIN, 1)

        # Log the result
        db.connect()
        log = Log(
            timestamp=dt.datetime.now(),
            humidity=state.humidity,
            temperature=state.temp,
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
