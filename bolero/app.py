from flask import Flask
from flask_restless import APIManager
from .trackers import db
import logging
from .utils import get_loaded_trackers, get_config_file
from . import tracker_classes
from .scheduler import scheduler
import os

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['AUTH_KEYS'] = dict()
app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ['SQL_URL'] or
                                         get_config_file()['sql_url'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Setup logging
logging.basicConfig(level="INFO")

manager = APIManager(app, flask_sqlalchemy_db=db)


def load_trackers():
    loaded_trackers = get_loaded_trackers()  # Load names of imported trackers

    # Filter enabled tracker object classes
    return [x for x in tracker_classes if x.__name__ in loaded_trackers or
            x.service_name in loaded_trackers]


def setup():
    db.init_app(app)

    for t in load_trackers():
        t_instance = t()
        t_instance.create_api(manager)

        # Add scheduled jobs for update / backfill
        scheduler.add_job(t_instance.update, trigger='interval',
                          **t_instance.update_interval)
        scheduler.add_job(t_instance.backfill, trigger='interval',
                          **t_instance.backfill_interval)
    # Initialize db tables
    with app.app_context():
        db.create_all()

# Load CLI commands
from . import cli

if __name__ == '__main__':
    setup()
    app.run(debug=True)
