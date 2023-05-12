# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
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
    active_station = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.station == "USC00519281").\
                filter(Measurement.date >= (dt.date(2017, 8, 18) - dt.timedelta(days=365))).all()
    
    session.close()

    tobs = []
    for date, tobs in active_station:
       tobs_dictionary={}
       tobs_dictionary['date'] = date
       tobs_dictionary['tobs'] = tobs
       tobs.append(tobs_dictionary)
    
    return jsonify(tobs)

# the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range
@app.route("/api/v1.0/<start>")
def start(date):
    
    avg = [func.min(Measurement.tobs),
               func.max(Measurement.tobs),
               func.avg(Measurement.tobs)]
    start_date = session.query(*avg).filter(Measurement.date >= date).all()

    return jsonify(start_date)

@app.route("/api/v1.0/<start>/<end>")
def start(start, end):
    
    avg = [func.min(Measurement.tobs),
               func.max(Measurement.tobs),
               func.avg(Measurement.tobs)]
    start_end_date = session.query(*avg).filter(Measurement.date >= start).\
        filter(Measurement.date >= end).all()

    return jsonify(start_end_date)
    

if __name__ == '__main__':
    app.run(debug=True)