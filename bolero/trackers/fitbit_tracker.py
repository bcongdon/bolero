import fitbit
from ..utils import requires
from . import db
from .tracker import BoleroTracker
import datetime


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

    def save_or_update(self, date=datetime.date.today()):
        day = self.client.activities(date=date)['summary']
        db_date = (FitbitDay.query.filter_by(date=date).first() or
                   FitbitDay(date=date))
        db_date.steps = day['steps']
        db_date.calories_burned = day['caloriesOut']
        db_date.floors = day['floors']
        db_date.lightly_active_minutes = day['lightlyActiveMinutes']
        db_date.fairly_active_minutes = day['fairlyActiveMinutes']
        db_date.very_active_minutes = day['veryActiveMinutes']
        db_date.miles = next(i for i in day['distances']
                             if i['activity'] == 'total')['distance']
        db.session.add(db_date)
        db.session.commit()

    def update(self):
        date = datetime.date.today()
        for i in range(7):
            self.save_or_update(date=date - datetime.timedelta(days=i))

    def create_api(self, manager):
        manager.create_api(FitbitDay)
