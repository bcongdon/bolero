from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restless import APIManager
import logging

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Setup logging
logging.basicConfig(level="INFO")

db = SQLAlchemy(app)

manager = APIManager(app, flask_sqlalchemy_db=db)

from trackers import *

db.create_all()
