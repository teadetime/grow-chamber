from peewee import *
import datetime as dt
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


db.connect()
db.create_tables([Control, Log])

test_log = Log(
    timestamp=dt.datetime.now(),
    humidity=33.4,
    temperature=22.2,
    humidity_status=True,
    fan_status=False,
)
test_log.save()

test_control = Control(
    timestamp=dt.datetime.now(),
    humidity_setpoint=25.4,
    fan_period=DEFAULT_AIR_PRD,
    fan_duration=DEFAULT_AIR_DURATION,
)

test_control.save()
print(Log.select().order_by(Log.timestamp.desc()).get().timestamp)
db.close()
