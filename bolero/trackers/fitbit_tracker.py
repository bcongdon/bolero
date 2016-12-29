import fitbit
from ..utils import requires
from ..scheduler import scheduler
from . import db
from .tracker import BoleroTracker
import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import logging
logger = logging.getLogger(__name__)

class FitbitDay(db.Model):
    date = db.Column(db.Date, primary_key=True)
    steps = db.Column(db.Integer)
    calories_burned = db.Column(db.Integer)
    floors = db.Column(db.Integer)
    lightly_active_minutes = db.Column(db.Integer)
    fairly_active_minutes = db.Column(db.Integer)
    very_active_minutes = db.Column(db.Integer)
    miles = db.Column(db.Float(precision=5))


class FitbitTracker(BoleroTracker):
    service_name = 'fitbit'

    @requires('fitbit.consumer_key', 'fitbit.consumer_secret',
              'fitbit.refresh_token', 'fitbit.access_token')
    def handle_authentication(self, config):
        return fitbit.Fitbit(config['fitbit.consumer_key'],
                             config['fitbit.consumer_secret'],
                             access_token=config['fitbit.access_token'],
                             refresh_token=config['fitbit.refresh_token'])

    def save_or_update(self, date, steps, caloriesOut, floors,
                       lightly_active_minutes, fairly_active_minutes,
                       very_active_minutes, distance):

        db_date = (FitbitDay.query.filter_by(date=date).first() or
                   FitbitDay(date=date))
        db_date.date = date
        db_date.steps = steps
        db_date.calories_burned = caloriesOut
        db_date.floors = floors
        db_date.lightly_active_minutes = lightly_active_minutes
        db_date.fairly_active_minutes = fairly_active_minutes
        db_date.very_active_minutes = very_active_minutes
        db_date.miles = distance
        db.session.add(db_date)
        db.session.commit()

    def fetch_day(self, date):
        day = self.client.activities(date=date)['summary']
        self.save_or_update(
            date,
            day['steps'],
            day['caloriesOut'],
            day['floors'],
            day['lightlyActiveMinutes'],
            day['fairlyActiveMinutes'],
            day['veryActiveMinutes'],
            next(i for i in day['distances']
                 if i['activity'] == 'total')['distance'])

    def save_range(self, start, end):
        attributes = ['steps', 'calories', 'floors', 'minutesLightlyActive',
                      'minutesFairlyActive', 'minutesVeryActive', 'distance']
        while start <= end:
            data = {}
            for a in attributes:
                res = self.client.time_series(
                    'activities/' + a,
                    period='1y',
                    base_date=start)
                data[a] = {i['dateTime']: i['value']
                           for i in res[res.keys()[0]]}
            dates = data['steps'].keys()
            for d in dates:
                self.save_or_update(
                    parse(d).date(),
                    data['steps'][d],
                    data['calories'][d],
                    data['floors'][d],
                    data['minutesLightlyActive'][d],
                    data['minutesFairlyActive'][d],
                    data['minutesVeryActive'][d],
                    data['distance'][d]
                )
            start += relativedelta(years=1)

    def update(self):
        date = datetime.date.today()
        for i in range(7):
            self.save_or_update(date=date - datetime.timedelta(days=i))

    def backfill(self):
        profile = self.client.user_profile_get()
        start = parse(profile['user']['memberSince']).date()
        self.save_range(start, datetime.date.today())

    def create_api(self, manager):
        manager.create_api(FitbitDay)
