from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restless import APIManager
import logging
import json
import importlib


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:@localhost'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Setup logging
logging.basicConfig(level="INFO")

db = SQLAlchemy(app)

manager = APIManager(app, flask_sqlalchemy_db=db)

# Import enabled trackers
with open('config.json') as f:
    loaded_trackers = json.load(f)['enabled_trackers']
    for t in loaded_trackers:
        importlib.import_module('.' + t, package='bolero.trackers')

db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
