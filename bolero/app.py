from flask import Flask
from flask_restless import APIManager
from .trackers import db
import logging
import importlib
from .utils import get_loaded_trackers, get_config_file
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['AUTH_KEYS'] = dict()
app.config['SQLALCHEMY_DATABASE_URI'] = get_config_file()['sql_url']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Setup logging
logging.basicConfig(level="INFO")

manager = APIManager(app, flask_sqlalchemy_db=db)


def setup():
    db.init_app(app)

    # Import enabled trackers
    loaded_trackers = get_loaded_trackers()
    for t in loaded_trackers:
        logger.info('Loading tracker: {}'.format(t))
        tracker = importlib.import_module('.trackers.' + t, 'bolero')
        # tracker.create_api()
    with app.app_context():
        db.create_all()


# Load CLI commands
from . import cli

if __name__ == '__main__':
    setup()
    app.run(debug=True)
