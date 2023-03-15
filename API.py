
from flask import Flask, jsonify
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
from sqlalchemy import create_engine, inspect
from datetime import datetime, timedelta
from sqlalchemy import func
import os
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
# View all of the classes that automap found
Base.classes.keys()
# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

app = Flask(__name__)

# 3. Define static routes (home)
@app.route("/")
def welcome():
    return (
        f"Welcome to my challenge API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"   
        f"/api/v1.0/<start>/<end><br/>"    
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    mostrecent_date = session.query(func.max(measurement.date)).scalar()
    mostrecent_date = datetime.strptime(mostrecent_date, '%Y-%m-%d').date()
    one_year_ago = mostrecent_date - timedelta(days=365)
    last_12_precipitation = session.query(measurement.date, measurement.prcp)\
        .filter(measurement.date >= one_year_ago)\
        .filter(measurement.date <= mostrecent_date)\
        .all()
    session.close()

    # Create a dictionary from the row data and append to a list of precipitation data
    last_12_precipitation_list = []
    for date, prcp in last_12_precipitation:
        last_12_precipitation_dict = {}
        last_12_precipitation_dict["date"] = date
        last_12_precipitation_dict["prcp"] = prcp
        last_12_precipitation_list.append(last_12_precipitation_dict)
    return jsonify(last_12_precipitation_list)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the station and date count for each station, ordered by the count in descending order
    stations = session.query(measurement.station, func.count(measurement.date))\
        .group_by(measurement.station)\
        .order_by(func.count(measurement.date).desc())\
        .all()

    session.close()

    # Create a dictionary from the row data and append to a list of station data
    station_list = []
    for station, count in stations:
        station_dict = {}
        station_dict["station"] = station
        station_dict["count"] = count
        station_list.append(station_dict)

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Using the most active station id
    mostrecent_date_USC00519281 = session.query(func.max(measurement.date)).filter(measurement.station == 'USC00519281').scalar()
    mostrecent_date_USC00519281 = datetime.strptime(mostrecent_date_USC00519281, '%Y-%m-%d').date()
    # calculate the date 12 months ago
    one_year_ago = mostrecent_date_USC00519281 - timedelta(days=365)
    
    # Query the last 12 months of temperature observation data for this station
    last_12_temp = session.query(measurement.date, measurement.tobs)\
        .filter(measurement.station == 'USC00519281')\
        .filter(measurement.date > one_year_ago)\
        .order_by(measurement.date)\
        .all()
    
    session.close()

    # Create a dictionary from the row data and append to a list of temperature data
    last_12_temp_list = []
    for date, tobs in last_12_temp:
        last_12_temp_dict = {}
        last_12_temp_dict["date"] = date
        last_12_temp_dict["tobs"] = tobs
        last_12_temp_list.append(last_12_temp_dict)

    return jsonify(last_12_temp_list)

@app.route("/api/v1.0/<start>")
def start_date_temps(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the min, max, and avg temperatures for all dates greater than or equal to the start date
    start_temps = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs))\
        .filter(measurement.date >= start)\
        .all()

    session.close()

    # Create a dictionary for the temperature data
    temp_dict = {}
    temp_dict["TMIN"] = start_temps[0][0]
    temp_dict["TMAX"] = start_temps[0][1]
    temp_dict["TAVG"] = start_temps[0][2]

    return jsonify(temp_dict)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Convert the start and end date strings to datetime objects
    start_date = datetime.strptime(start, '%Y-%m-%d').date()
    end_date = datetime.strptime(end, '%Y-%m-%d').date()

    # Query the minimum, maximum, and average temperature for the date range specified
    temperature_data = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs))\
        .filter(measurement.date >= start_date)\
        .filter(measurement.date <= end_date)\
        .all()

    session.close()

    # Create a dictionary to store the temperature data
    temperature_dict = {}
    temperature_dict['start_date'] = start_date
    temperature_dict['end_date'] = end_date
    temperature_dict['TMIN'] = temperature_data[0][0]
    temperature_dict['TMAX'] = temperature_data[0][1]
    temperature_dict['TAVG'] = temperature_data[0][2]

    return jsonify(temperature_dict)


if __name__ == "__main__":
    app.run(debug=True)
