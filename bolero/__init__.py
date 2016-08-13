from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restless import APIManager

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from trackers import *

db.create_all()

manager = APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(trackers.twitter.Tweet,  methods=['GET', 'POST'])

trackers.twitter.get_tweets()
