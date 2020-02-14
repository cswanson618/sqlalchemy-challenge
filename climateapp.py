from flask import Flask, escape, request, jsonify
from matplotlib import style

style.use("fivethirtyeight")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct, desc
from pprint import pprint

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

app = Flask(__name__)


@app.route("/")
def SplashPage():
    return "Welcome to the Climate App."


precip_data = (
    session.query(Measurement.prcp, Measurement.date)
    .filter(
        Measurement.date >= dt.date(2016, 8, 23),
        Measurement.date <= dt.date(2017, 8, 23),
    )
    .all()
)
df_meas_precipdata_unclean = pd.DataFrame(
    precip_data, columns=["Precipitation", "Date"]
).dropna()
df_meas_precipdata_date_unclean = df_meas_precipdata_unclean["Date"]
df_meas_precipdata_date_clean = pd.DataFrame(
    pd.to_datetime(df_meas_precipdata_date_unclean)
)
df_meas_precipdata_precip = df_meas_precipdata_unclean["Precipitation"]
df_meas_precipdata_precipdf = pd.DataFrame(df_meas_precipdata_precip)
df_meas_precipdata_clean = df_meas_precipdata_date_clean.join(
    df_meas_precipdata_precipdf
)


@app.route("/api/v1.0/precipitation")
def PrecipQuery():
    precip_json = df_meas_precipdata_clean.to_json(date_format="iso", orient="records")
    return precip_json


active_stations = (
    session.query(Measurement.station, func.count(Measurement.station))
    .group_by(Measurement.station)
    .order_by(desc(func.count(Measurement.station)))
    .all()
)
stations_df = pd.DataFrame(active_stations, columns=["Station", "Number of Measures"])


@app.route("/api/v1.0/stations")
def StationsQuery():
    stations_json = stations_df.to_json(orient="records")
    return stations_json


if __name__ == "__main__":
    app.run(debug=True)
