# Import dependencies
from datetime import datetime
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

import datetime as dt
import pandas as pd
from flask import Flask, jsonify

# Setup database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

session = Session(engine)
# Entry of the last date
date_eof = session.query(Measurement.date).order_by(
    Measurement.date.desc()).first()
# A year before last entry
previous_year = dt.datetime.strptime(
    date_eof[0], '%Y-%m-%d') - dt.timedelta(days=365)
session.close()

# Flask Routes

@app.route("/")
def index():
    #Available Api's
    return (f"Available Routes:<br/><hr>"
        f"<a href='/api/v0.1/precipitation'>Precipitation<br/>"
        f"<a href='/api/v0.1/stations'>Available Stations<br/>"
        f"<a href='/api/v0.1/tobs'>Temperature at the time of observation<br/>"
        f"<a href='/api/v0.1/start'>Start date temperature<br/>"
        f"<a href='/api/v0.1/start-end'>End date temperature<br/>")

@app.route("/api/v0.1/precipitation")
def precipitation():
    # Session link to db
    session = Session(engine)

    # Precipitation query for the last year
    precip_last_year = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > previous_year).all()

    session.close()

    # Store results in dictionary
    precipitation_dict = []
    for date, prcp in precip_last_year:
        row = {}
        row['date'] = date
        row['prcp'] = prcp
        precipitation_dict.append(row)

    # Return dictionary as JSON
    return jsonify(precipitation_dict)

@app.route("/api/v0.1/stations")
def stations():
    # Session link to db
    session = Session(engine)

    # Query all stations
    results = session.query(Station.station, Station.name).all()

    session.close()

    # Store results in dictionary
    all_stations = []
    for station, name in results:
        row = {}
        row['station'] = station
        row['name'] = name
        all_stations.append(row)

    return jsonify(all_stations)

@app.route("/api/v0.1/tobs")
def tobs():
    # Session link to db
    session = Session(engine)

    # Query the highest tobs station
    most_active = session.query(Station.station, func.count(Station.station)).\
        group_by(Station.station).\
        order_by(func.count(Station.station).desc()).first()[0]
    
    # Using the station id from the previous query, calculate the lowest temperature recorded,
    # highest temperature recorded, and average temperature of the most active station?
    results = session.query(Measurement.station, Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active)\
        .filter(Measurement.date >= previous_year).all()
    session.close()
    # Store results in dictionary
    tobs_dict = []
    for station, date,tobs in results:
        row = {}
        row['station'] = station
        row['date'] = date
        row['tobs'] = tobs
        tobs_dict.append(row)
    return jsonify(tobs_dict)

#@app.route("/api/v0.1/start")
#@app.route("/api/v0.1/start-end")

if __name__ == '__main__':
    app.run(debug=True)
