import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

version = "v1.0"


#######################
# Database Setup
#######################
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#######################
# Flask App Setup
#######################
app = Flask(__name__)

# Route paths
precip_route = f"/api/{version}/precipitation"
stations_route = f"/api/{version}/stations"
tobs_route = f"/api/{version}/tobs"
temp_start_end_route = f"/api/{version}/temp/start/end"


@app.route("/")
def welcome():
    return f"""
        Welcome to the Climate Analysis API!
        Available Routes:
        {precip_route}
        {stations_route}
        {tobs_route}
        {temp_start_end_route}
        """


@app.route(precip_route)
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = (
        session.query(Measurement.date, Measurement.prcp)
        .filter(Measurement.date >= prev_year)
        .all()
    )
    precip = {date: prcp for date, prcp in precipitation}

    return jsonify(precip)


@app.route(stations_route)
def stations():
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)


@app.route(tobs_route)
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = (
        session.query(Measurement.tobs)
        .filter(Measurement.station == "USC00519281")
        .filter(Measurement.date >= prev_year)
        .all()
    )
    temps = list(np.ravel(results))
    return jsonify(temps=temps)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    sel = [
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs),
    ]

    if not end:
        results = session.query(*sel).filter(Measurement.date >= start).all()

        temps = list(np.ravel(results))
        return jsonify(temps)

    results = (
        session.query(*sel)
        .filter(Measurement.date >= start)
        .filter(Measurement.date <= end)
        .all()
    )
    temps = list(np.ravel(results))

    return jsonify(temps)
