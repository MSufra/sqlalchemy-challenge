#import libraries
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

# Database Setup
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)


Station = Base.classes.station
Measurement = Base.classes.measurement
#last 12 months of data
start_date = dt.datetime(2017,8,23) - dt.timedelta(days=366)
# Flask Setup
app = Flask(__name__)


#ROUTES

#home
@app.route("/")
def home():
    return (
        f"Available Routes<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperature Observations: /api/v1.0/tobs<br/>"
        f"Temperature Min/Max/AVG for Date Range : /api/v1.0/start date/end date<br/>"
        f"Dates Must be given as YYYY-MM-DD format<br/>"
        f"End Date defaults to last data point if not given"
    )


#precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    #retrivee data
    session = Session(bind=engine)
    data = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= start_date).all()
    session.close()
    #create dictionary
    all_prcp = []
    for date, prcp in data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)
    #return data
    return jsonify(all_prcp)

#stations
@app.route('/api/v1.0/stations')
def stations():
    #retrieve data
    session = Session(bind=engine)
    data = session.query(Station.station).all()
    session.close()
    all_stations = list(np.ravel(data))
    #return data
    return jsonify(all_stations)

#tobs
@app.route("/api/v1.0/tobs")
def tobs():
    #retrieve data
    session = Session(bind=engine)
    data = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= start_date, Measurement.station =='USC00519281').all()
    session.close()
    
    all_tobs = []
    for date, tobs in data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)
    
    return jsonify(all_tobs)



@app.route('/api/v1.0/<start>')
def start(start):
    try:
        #convert start to datetime
        start =  dt.datetime.strptime(start,'%Y-%m-%d')
        #retrieve data
        session = Session(bind=engine)
        data = session.query(func.min(Measurement.tobs),
                  func.max(Measurement.tobs),
                  func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
        session.close()

        stats = list(np.ravel(data))
        #return data
        return jsonify(stats)
    
    except:
        return "error: date not found, 404"

@app.route('/api/v1.0/<start>/<end>')
def start_end(start,end):
    try:
    #convert start to datetime
        start =  dt.datetime.strptime(start,'%Y-%m-%d')
        end =  dt.datetime.strptime(end,'%Y-%m-%d')
        #retrieve data
        session = Session(bind=engine)
        data = session.query(func.min(Measurement.tobs),
                  func.max(Measurement.tobs),
                  func.avg(Measurement.tobs)).filter(Measurement.date >= start, Measurement.date <= end).all()
        session.close()

        stats = list(np.ravel(data))
        #return data
        return jsonify(stats)
    
    except:
        return "error: date not found, 404"

    if __name__ == '__main__':
    app.run(debug=True)