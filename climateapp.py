from flask import Flask, escape, request, jsonify
from matplotlib import style

style.use("fivethirtyeight")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime
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
    return (
        f"Welcome to The Climate App<br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation which returns precipitation in Hawaii by date from 2016-08-23 to 2017-08-23<br/>"
        f"/api/v1.0/stations which returns unique measuring stations in Hawaii and how many measurements they recorded<br/>"
        f"/api/v1.0/temps/START which returns temperature measures from the most active station beginning at <start> date*<br/>"
        f"/api/v1.0/temps/START/END which returns temperature measures from the most active station beginning at START date* and ending at END date*<br/>"
        f"<br/>"
        f"<b>*IMPORTANT NOTE: Dates MUST be formatted YYYY-MM-DD</b>"
    )


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


temp_active = (
    session.query(Measurement.station, Measurement.tobs, Measurement.date)
    .filter(Measurement.station == "USC00519281")
    .filter(
        Measurement.date >= dt.date(2016, 8, 23),
        Measurement.date <= dt.date(2017, 8, 23),
    )
    .all()
)
temp_active_df_unclean = pd.DataFrame(temp_active)
temp_active_date = temp_active_df_unclean["date"]
temp_active_date_clean = pd.DataFrame(pd.to_datetime(temp_active_date))
temp_active_df_unclean2 = temp_active_df_unclean
temp_active_df_unclean3 = temp_active_df_unclean2.drop(columns="date")
temp_active_df = temp_active_df_unclean3.join(temp_active_date_clean)


@app.route("/api/v1.0/temps/<start>")
def TempQuery(start):
    date_list = []
    for index, row in temp_active_df.iterrows():
        if row["date"] >= datetime.strptime(start, "%Y-%m-%d"):
            date_list.append((row["date"], row["tobs"]))
    return jsonify(date_list)


@app.route("/api/v1.0/temps/<start>/<end>")
def TempQuerySE(start, end):
    date_list = []
    for index, row in temp_active_df.iterrows():
        if row["date"] >= datetime.strptime(start, "%Y-%m-%d") and row[
            "date"
        ] <= datetime.strptime(end, "%Y-%m-%d"):
            date_list.append((row["date"], row["tobs"]))
    return jsonify(date_list)


if __name__ == "__main__":
    app.run(debug=True)
