from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restless import APIManager
import logging
import json
import importlib
from .utils import get_loaded_trackers
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['AUTH_KEYS'] = dict()
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:@localhost'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Setup logging
logging.basicConfig(level="INFO")

db = SQLAlchemy(app)

manager = APIManager(app, flask_sqlalchemy_db=db)


def setup():
    # Import enabled trackers
    loaded_trackers = get_loaded_trackers()
    for t in loaded_trackers:
        logger.info('Loading tracker: {}'.format(t))
        importlib.import_module('.trackers.' + t, 'bolero')

    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
