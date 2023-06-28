# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt
from dateutil.parser import parse

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)




#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.

#Return the JSON representation of your dictionary.
    date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date[0]
    results_date = pd.to_datetime(date[0]) - dt.timedelta(days=365)
    results_date_df= results_date.date()

    results_date = session.query(Measurement.date,Measurement.prcp).all()
    one_year = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= results_date_df)
    one_year_df = pd.DataFrame(one_year)
    one_year_df.rename(columns={"date":"Date","prcp":"Precipitation"},inplace=True) 
    precip_dict = one_year_df.to_dict('index')
    return jsonify(precip_dict)

    session.close()

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    
    station_inv = session.query(Station.station).all()

    # Close Session
    session.close()

    all_stations = list(np.ravel(station_inv))
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def active_station():
# Create our session (link) from Python to the DB
    session = Session(engine)
    date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date[0]
    year_ago = pd.to_datetime(date[0]) - dt.timedelta(days=365)
    yearago = year_ago.date()
    most_act_st_id = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    yearago_tobs = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= yearago).filter(Measurement.station == most_act_st_id)
    tobs_yearago_df = pd.DataFrame(yearago_tobs)
    tobs_yearago_df.rename(columns={"date":"Date","tobs":"tobs"},inplace=True) 
    tobs_yearago_sorted = tobs_yearago_df.sort_values(by="Date")
    
# Close Session
    session.close()
    tobs_yearago_list = list(np.ravel(tobs_yearago_sorted.to_dict('index')))
    return jsonify(tobs_yearago_list)

@app.route("/api/v1.0/<start>")
def date_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Change the date in string format to datatime.date
    query_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    
    # Set up the list for query
    temp_list = [func.min(Measurement.tobs), 
                func.max(Measurement.tobs), 
                func.avg(Measurement.tobs)]

    # Filter out the measurements between the query date
    date_temp = session.query(*temp_list).\
                filter(func.strftime('%Y-%m-%d', Measurement.date) >= query_date).all()
    
    # Close Session
    session.close()
    # Create a dictionary from the row data and append to a list

    return (
        f"Analysis of temperature from {start} to 2017-08-23 (the latest measurement in database):<br/>"
        f"Minimum temperature: {round(date_temp[0][0], 1)} °F<br/>"
        f"Maximum temperature: {round(date_temp[0][1], 1)} °F<br/>"
        f"Average temperature: {round(date_temp[0][2], 1)} °F"
    )



@app.route("/api/v1.0/<start>/<end>")
def date_start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Change the date in string format to datatime.date
    query_date_start = dt.datetime.strptime(start, '%Y-%m-%d').date()
    query_date_end = dt.datetime.strptime(end, '%Y-%m-%d').date()
    
    # Set up the list for query
    temp_list = [func.min(Measurement.tobs), 
                func.max(Measurement.tobs), 
                func.avg(Measurement.tobs)]

    # Pick out the measurements between the query date
    date_temp = session.query(*temp_list).\
                filter(func.strftime('%Y-%m-%d', Measurement.date) >= query_date_start).\
                filter(func.strftime('%Y-%m-%d', Measurement.date) <= query_date_end).all()
    
    # Close Session
    session.close()

    return (
        f"Analysis of temperature from {start} to {end}:<br/>"
        f"Minimum temperature: {round(date_temp[0][0], 1)} °F<br/>"
        f"Maximum temperature: {round(date_temp[0][1], 1)} °F<br/>"
        f"Average temperature: {round(date_temp[0][2], 1)} °F"
    )



if __name__ == '__main__':
    app.run(debug=True)