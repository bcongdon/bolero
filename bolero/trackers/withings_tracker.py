from ..utils import requires
import logging
from ..app import manager
from . import db
from ..scheduler import scheduler
from withings import WithingsApi, WithingsCredentials
logger = logging.getLogger(__name__)


class Measurement(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    date = db.Column(db.DateTime(timezone=False))
    weight = db.Column(db.Float(precision=5))

    @staticmethod
    def save_or_update(m):
        measure = (Measurement.query.filter(
                   Measurement.id == m.grpid).first() or
                   Measurement(id=m.grpid))
        measure.date = m.date
        measure.weight = m.weight
        db.session.add(measure)
        db.session.commit()


@requires('withings.access_token', 'withings.access_token_secret',
          'withings.consumer_key', 'withings.consumer_secret',
          'withings.user_id')
def handle_authentication(config):
    config = {x.split('.')[1]: config[x] for x in config}
    creds = WithingsCredentials(**config)
    return WithingsApi(creds)


# @scheduler.scheduled_job('interval', hours=1)
def get_measurements():
    """
    Saves all measurements (weight, body fat, etc) for the authenticated user
    """
    api = handle_authentication()
    measures = api.get_measures()
    for m in filter(lambda t: t.weight, measures):
        Measurement.save_or_update(m)


def create_api():
    manager.create_api(Measurement)
