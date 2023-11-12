from peewee import *
import datetime as dt

from constants import (
    DBNAME,
    DEFAULT_AIR_PRD,
    DEFAULT_HUMIDITY,
    DEFAULT_AIR_DURATION,
)

db = SqliteDatabase(DBNAME)


class Control(Model):
    timestamp = DateTimeField()
    humidity_setpoint = FloatField()
    fan_period = IntegerField()
    fan_duration = IntegerField()

    class Meta:
        database = db


class Log(Model):
    timestamp = DateTimeField()
    humidity = FloatField()
    temperature = FloatField()
    humidity_status = BooleanField()
    fan_status = BooleanField()

    class Meta:
        database = db


def db_setup() -> None:
    db.connect()
    db.create_tables([Control, Log])
    if not Control.get_or_none():
        Control.create(
            timestamp=dt.datetime.now(),
            humidity_setpoint=DEFAULT_HUMIDITY,
            fan_period=DEFAULT_AIR_PRD,
            fan_duration=DEFAULT_AIR_DURATION,
        ).save()
    db.close()


class State:
    def __init__(self, humidity=40.0, temp=20.0) -> None:
        self.fan_on: bool = False
        self.humid_on: bool = False
        self.humidity: float = humidity
        self.temp: float = temp
