from os import path
from datetime import datetime

import sqlite3

from constants import DB_CTL_TBL, DB_LOG_TBL, DBNAME, DEFAULT_AIR_MIN, DEFAULT_HUMIDITY

def database_setup() -> None:
  con = sqlite3.connect(DBNAME)
  cur = con.cursor()

  control_tbl = cur.execute(f"SELECT * FROM sqlite_master WHERE name ='{DB_CTL_TBL}' and type='table'").fetchone() 
  log_tbl= cur.execute(f"SELECT * FROM sqlite_master WHERE name = '{DB_LOG_TBL}' and type='table'").fetchone() 
  if control_tbl is None:
    cur.execute(f"CREATE TABLE IF NOT EXISTS {DB_CTL_TBL} \
         (timestamp TIMESTAMP PRIMARY KEY     NOT NULL,\
         humidity            REAL     NOT NULL,\
         air            INT     NOT NULL);")
  if log_tbl is None:
    cur.execute(f"CREATE TABLE IF NOT EXISTS {DB_LOG_TBL} \
         (timestamp TIMESTAMP PRIMARY KEY     NOT NULL, \
         humidity            REAL     NOT NULL, \
         temp                 REAL     NOT NULL, \
         humidifier_status   INT     NOT NULL, \
         air_status            INT     NOT NULL);")
  # Check that control has an entry
  control_pts = cur.execute(f"SELECT * FROM {DB_CTL_TBL}").fetchone() 
  if control_pts is None:
    cur.execute(f"INSERT INTO {DB_CTL_TBL} VALUES \
         ('{datetime.now()}', {DEFAULT_HUMIDITY}, {DEFAULT_AIR_MIN});")

  # Close and commit to the DB
  con.commit()
  cur.close()
  con.close()

if __name__ == "__main__":
  database_setup()
