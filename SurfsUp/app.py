import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite

engine = create_engine("sqlite:///Resources/hawaii.sqlite",echo=False)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Station= Base.classes.station
Measurement= Base.classes.measurement

#################################################
# Flask Setup
#################################################
app=Flask(__name__)

#################################################
# Flask Routes 1,showing all available routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
        f"Please Note: the date should be input using format:YYYY-mm-dd or YYYY-mm-dd/YYYY-mm-dd"
    )
#################################################
# Flask Routes 2, showing date as the key and prcp as the value
#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitation (prcp) and date (date) data"""
    
    # Create new variable to store results from query to Measurement table for prcp and date columns
    prcp_data_query = session.query(Measurement.date, Measurement.prcp).all()

    # Close session
    session.close()
    prcp_data = []
    for date,prcp in prcp_data_query:
        prcp_dict = {}
        prcp_dict['date'] =date
        prcp_dict['prcp'] =prcp
        
        # prcp_dict["precipitation"] = prcp
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data) 

#################################################
# Flask Routes 3: Return a JSON list of stations from the dataset.
#################################################

@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all station names"""
    # Query all stations names
    station_query = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    station_data = []
    for station in station_query:
        station_dict = {}
        station_dict["station"] =station
       
        station_data.append(station_dict)

    return jsonify(station_data) 

#################################################
# Flask Routes 4: Return a JSON list of stations from the dataset.
#################################################
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of dates and temperature observations of the most-active station for the previous year of data. """
    # get the most recent date in the dataset
    most_recent_date = session.query(Measurement.date).\
                                     order_by(Measurement.date.desc()).first() 
    print(f'The most recent date is {most_recent_date}')
    start_date='2016-08-23'
    print(f'The start date is {start_date}')
   
    #Get the most activate station in the dataset
    most_active_station=session.query(Measurement.date,Measurement.station).\
                            group_by(Measurement.station).\
                            order_by(func.count(Measurement.station).desc()).first()
    print(f'The most activate staion is {most_active_station.station}')
    #get dates and temperature observations in the most activate station last year in the dataset
    most_active_station_resouce=session.query(Measurement.date,Measurement.tobs).\
                                        filter(Measurement.station==most_active_station).\
                                        filter(Measurement.date>start_date)
    most_active_station_resouce
    session.close()

    # Create a dictionary of dates,tobs,and stations that will be appended with dictionary values for date, tobs, and station number queried above
    dates_tobs_last_year_data = []
    for date, tobs, station in most_active_station_resouce:
        dates_tobs_dict = {}
        dates_tobs_dict["date"] = date
        dates_tobs_dict["tobs"] = tobs
        dates_tobs_dict["station"] = station
        dates_tobs_last_year_data.append(dates_tobs_dict)
        
    return jsonify(dates_tobs_last_year_data) 

#################################################
# Flask Routes 5: Return a JSON list of min, avg, max temperature from the dataset.
#################################################

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """ Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start """
    # Using the most active station id from the previous query, calculate the lowest, average, and highest temperature.
    startdate_tobs_resource=session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
                                    filter(Measurement.date>=start).all()
    startdate_tobs_resource
    session.close()
     # Create a dictionary of dates,tobs,and stations that will be appended with dictionary values for min, avg, and max temperature queried above
    startdate_tobs_data=[]
    for min, avg, max in startdate_tobs_resource:
        startdate_tobs_dict={}
        startdate_tobs_dict['TMIN']=min
        startdate_tobs_dict['TAVG']=avg
        startdate_tobs_dict['TMAX']=max
        startdate_tobs_data.append(startdate_tobs_dict)
    return jsonify(startdate_tobs_data) 


@app.route("/api/v1.0/<start>/<end>")
def startend_date(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """ Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start """
    # Using the most active station id from the previous query, calculate the lowest, average, highest temperature.
    start_end_date_tobs_resource=session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
                                    filter(Measurement.date>=start).\
                                    filter(Measurement.date<=end).all()
    start_end_date_tobs_resource
    session.close()
    # Create a dictionary of dates,tobs,and stations that will be appended with dictionary values for min, avg, and max temperature queried above
    start_end_date_tobs_data=[]
    for min, avg, max in start_end_date_tobs_resource:
        start_end_date_tobs_dict={}
        start_end_date_tobs_dict['TMIN']=min
        start_end_date_tobs_dict['TAVG']=avg
        start_end_date_tobs_dict['TMAX']=max
        start_end_date_tobs_data.append(start_end_date_tobs_dict)
    return jsonify(start_end_date_tobs_data) 

if __name__=="__main_":
    app.run(debug=True)
