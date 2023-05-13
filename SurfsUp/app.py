# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///SurfsUp/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes for Hawaii."""
    return (
        f"Available Routes for Hawaii Weather API:<br/>"
        f"/api/v1.0/precipitation<br/>Returns list of percipitation data for the dates between 2016-08-23 and 2017-08-23<br/><br/>"
        f"/api/v1.0/stations<br/>Returns a JSON list of stations<br/><br/>"
        f"/api/v1.0/tobs<br/>Returns dates and temperature observations of the most-active station for the previous year<br/><br/>"
        f"/api/v1.0/<start><br/>Returns the minimum temperature, the average temperature, and the maximum temperature for a given start date (YYYY-MM-DD)<br/><br/>"
        f"/api/v1.0/<start>/<end><br/>Returns the minimum temperature, the average temperature, and the maximum temperature for a specified start and start-end range<br/><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Convert the query results from your precipitation analysis to dictionary

    last_data = [Measurement.date, 
       Measurement.prcp]
    last_year = session.query(*last_data).\
    filter(Measurement.date >= "2016-08-23").all()

    session.close()

    # create a dictionary
    precipitation = []
    for date, prcp in last_year:
       prcp_dictionary={}
       prcp_dictionary['date'] = date
       prcp_dictionary['prcp'] = prcp
       precipitation.append(prcp_dictionary)
    
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():

    # Query all stations
    results = session.query(Station.station, Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    
    # the most active station is USC00519281, the latest date of station tobs is 2017-08-18
    active_station = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
                filter(Measurement.station == "USC00519281").\
                filter(Measurement.date >= "2016-08-23").all()
    
    session.close()

    all_tobs = list(np.ravel(active_station))
    
    return jsonify(all_tobs)

# the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range
@app.route("/api/v1.0/<start>")
def startdate(start):
    
    begin_date = dt.datetime.strptime(start, "%y-%m-%d")
    last_tweleve_months = dt.timedelta(days=365)
    start = begin_date - last_tweleve_months
    end =  dt.date(2017, 8, 23)
    query_data_startdate = session.query(func.min(Measurement.tobs),
                               func.max(Measurement.tobs),
                               func.avg(Measurement.tobs)).filter(Measurement.date >= start).\
                                filter(Measurement.date <= end).all()
    startresults = list(np.ravel(query_data_startdate))
    return jsonify(startresults)
    

@app.route("/api/v1.0/<start>/<end>")
def startEndDate(start,end):

    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end = end_date-last_year
    start_end_date = session.query(func.min(Measurement.tobs),
                                   func.max(Measurement.tobs),
                                   func.avg(Measurement.tobs)).\
                                    filter(Measurement.date >= start).\
                                        filter(Measurement.date <= end).all()
    startendresult = list(np.ravel(start_end_date))

    return jsonify(startendresult)
    

if __name__ == '__main__':
    app.run()