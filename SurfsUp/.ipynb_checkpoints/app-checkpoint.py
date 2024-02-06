# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

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
# 1. /
#   Start at the homepage.
#   List all the available routes.
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate Analysis for Hawaii API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )


# 2. /api/v1.0/precipitation
#   Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
#   Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipation():
    session = Session(engine)
    last_twelve_months = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    one_year_ago = dt.date(last_twelve_months.year, last_twelve_months.month, last_twelve_months.day)
    date_prcp_scores = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).order_by(Measurement.date).all()
    prcp_dict = dict(date_prcp_scores)

    return jsonify(prcp_dict)


# 3. /api/v1.0/stations
#   Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    session.close()

    all_stations = []
    for station, name, latitude, longitude, elevation in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        all_stations.append(station_dict)
        
    return jsonify(all_stations)


# 4. /api/v1.0/tobs
#   Query the dates and temperature observations of the most-active station for the previous year of data.
#   Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= '2016-08-23').all()

    tobs = []
    for date, tobs_ in results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Temperature Observation"] = tobs_
        tobs.append(tobs_dict)

    return jsonify(tobs)


# 5. /api/v1.0/<start> and /api/v1.0/<start>/<end>
#   Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
#   For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
#   For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/<start>")
def start_temps(start):
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.station >= start).all()
    session.close()

    temperatures = []
    for temp_min, temp_avg, temp_max in results:
        temp_dict = {}
        temp_dict["Minimum Temperature"] = temp_min
        temp_dict["Average Temperature"] = temp_avg
        temp_dict["Maximum Temperature"] = temp_max
        temperatures.append(temp_dict)
        
    return jsonify(temperatures)


@app.route("/api/v1.0/<start>/<end>")
def start_end_temps(start, end):
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.station >= start).filter(Measurement.date <= end).all()
    session.close()

    temperatures = []
    for temp_min, temp_avg, temp_max in results:
        temp_dict = {}
        temp_dict["Minimum Temperature"] = temp_min
        temp_dict["Average Temperature"] = temp_avg
        temp_dict["Maximum Temperature"] = temp_max
        temperatures.append(temp_dict)
        
    return jsonify(temperatures)




if __name__ == "__main__":
    app.run(debug=True)