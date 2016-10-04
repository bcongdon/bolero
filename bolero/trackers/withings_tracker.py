from ..utils import requires
import logging
from . import db
from ..scheduler import scheduler
from .tracker import BoleroTracker
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


class WithingsTracker(BoleroTracker):
    service_name = 'withings'

    @requires('withings.access_token', 'withings.access_token_secret',
              'withings.consumer_key', 'withings.consumer_secret',
              'withings.user_id')
    def handle_authentication(self, config):
        config = {x.split('.')[1]: config[x] for x in config}
        creds = WithingsCredentials(**config)
        return WithingsApi(creds)

    def update(self):
        self.get_measurements()

    def get_measurements(self):
        """
        Saves all measurements (weight, body fat, etc) for the authenticated
        user
        """
        api = self.client
        measures = api.get_measures()
        for m in filter(lambda t: t.weight, measures):
            Measurement.save_or_update(m)

    def create_api(self, manager):
        manager.create_api(Measurement)
