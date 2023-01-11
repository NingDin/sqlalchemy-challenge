import numpy as np


import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# #################################################
# # Flask Setup
# #################################################
app = Flask(__name__)
#
#
# #################################################
# # Flask Routes
# #################################################
#
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"put date to replace start/end date below link:"
        f"<br/>"
        f"/api/v1.0/start<br/>"                    
        f"/api/v1.0/start/end</br>"
        f"input should be: YYYY-MM-DD"
        )
# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data)
# to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # link to DB
    session = Session(engine)
    past12mth = dt.date(2017,8,23) - dt.timedelta(days=364)
    print(past12mth)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= past12mth).all()
    session.close()
# return a jsonified list
    prcp_list=[{date:prcp} for date,prcp in results]
    return jsonify(prcp_list)

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def station():
    #link to DB
    session = Session(engine)
    stationresult=session.query(Station.station, Station.id).all()
    session.close()
# return a jsonified list
    station_list=[{id:station} for id, station in stationresult]
    return jsonify(station_list)
# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
    # link to DB
    session = Session(engine)
    # previous year assume mean fro most recent year (end 2017-08-23) ---refer to Jupyter file
    begindate = dt.date(2017,8, 23)-dt.timedelta(days=365)
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)). \
        order_by(func.count(Measurement.station).desc()). \
        group_by(Measurement.station).first()[0]
    mostAvtStationtobs = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).filter(Measurement.date>=begindate)
    session.close()
    tobs_list = [{date: tobs} for date, tobs in mostAvtStationtobs]
    return jsonify(tobs_list)

# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.

@app.route("/api/v1.0/<start>")
def start(start):
    # link to DB
    session=Session(engine)
    startresult=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date>= start).all()
    session.close()
    #create a list jsonified
    start_list=[]
    for min,avg,max in startresult:
        startdict={}
        startdict['Min tobs']= min
        startdict['Avg tobs']=avg
        startdict['Max tobs']=max
        start_list.append(startdict)
    return jsonify(start_list)

# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
## Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    #link to DB
    session=Session(engine)
    start_end_query=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date>=start).filter(Measurement.date<= end).all()
    session.close()

    start_end_list=[]
    for min, avg, max in start_end_query:
        rowdict={}
        rowdict['Min tobs']=min
        rowdict['Avg tobs']=avg
        rowdict['Max tobs']=max
        start_end_list.append(rowdict)

    return jsonify(start_end_list)

if __name__ == '__main__':
    app.run(debug=True)


