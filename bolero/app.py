from flask import Flask
from flask_restless import APIManager
from .trackers import db
from . import trackers
import logging
from .utils import get_loaded_trackers, get_config_file
from .scheduler import scheduler

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

    loaded_trackers = get_loaded_trackers()  # Load names of imported trackers

    # Filter enabled tracker object classes
    tracker_objects = [x for x in trackers if x.__name__ in loaded_trackers or
                       x.service_name in loaded_trackers]
    for t in tracker_objects:
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
