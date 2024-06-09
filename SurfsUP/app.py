# Import the dependencies.

from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
# connect to database
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# Home Route
@app.route("/")
def home():
    return(
        f"<center><h1>Hawaii Climate Analysis Local API<h1></center>"
        f"<center><h3>Select from the available routes:<h3></center>"
        f"<center>/api/v1.0/precipitation</center>"
        f"<center>/api/v1.0/stations</center>"
        f"<center>/api/v1.0/tobs</center>"
        f"<center>/api/v1.0/start/end</center>"
    )

# /api/v1.0/precipitation route
@app.route("/api/v1.0/precipitation")
def precip():
    # return the previous year's precipitation as a json
    # Calculate the date one year from the last date in data set.
    PreviousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= PreviousYear).all()

    session.close()

    # dictionary- date=key / prcp=value
    precipitation = {date: prcp for date, prcp in results}
    
    # convert to json
    return jsonify(precipitation)

# /api/v1.0/stations route
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    session.close()

    stationList = list(np.ravel(results))

    # convert to json
    return jsonify(stationList)

# /api/v1.0/tobs route
@app.route("/api/v1.0/tobs")
def temperatures():
    # Calculate the date one year from the last date in data set.
    PreviousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the temps fromt he most active station from the past year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= PreviousYear).all()

    session.close()

    temperatureList = list(np.ravel(results))
    return jsonify(temperatureList)

# /api/v1.0/start/end and /api/v1.0/start routes
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def dateStats(start=None, end=None):
     
    selection = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]

    if not end:

        startDate = dt.datetime.strptime(start, "%m%d%Y")

        results = session.query(*selection).filter(Measurement.date >= startDate).all()

        session.close()

        temperatureList = list(np.ravel(results))

        return jsonify(temperatureList)

    else:
        
        startDate = dt.datetime.strptime(start, "%m%d%Y")
        endDate = dt.datetime.strptime(end, "%m%d%Y")

        results = session.query(*selection).filter(Measurement.date >= startDate).filter(Measurement.date <= endDate).all()

        session.close()

        temperatureList = list(np.ravel(results))

        return jsonify(temperatureList)

# App Launcher
if __name__ == "__main__":
    app.run(debug=True)
