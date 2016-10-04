import myfitnesspal
from ..utils import requires
from . import db
from datetime import date, timedelta
from .tracker import BoleroTracker
from collections import defaultdict

foods_tbl = db.Table('food_join',
                     db.Column('food_id', db.Integer,
                               db.ForeignKey('mfpfood.id')),
                     db.Column('day_date', db.Date,
                               db.ForeignKey('mfpday.date')),
                     db.Column('id', db.Integer, primary_key=True)
                     )


class MFPFood(db.Model):
    """
    A unique 'food_type + quantity' model object. De-duplicated and referenced
    by 'foods_tbl' to save disk space in the database.
    """
    __tablename__ = 'mfpfood'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    calories = db.Column(db.Integer)
    carbohydrates = db.Column(db.Integer)
    fat = db.Column(db.Integer)
    protein = db.Column(db.Integer)
    sodium = db.Column(db.Integer)
    sugar = db.Column(db.Integer)

    @staticmethod
    def identical_food(f):
        """ Returns an identical MFPFood object if one exists """
        food_q = MFPFood.query.filter(MFPFood.name == f.name)
        if not food_q.first():
            return False
        for potential in food_q:
            if (all(f.totals[key] == getattr(potential, key)
                    for key in f.totals)):
                return potential

    @staticmethod
    def save_food(f):
        """ Does a 'get_or_save' style save for a python-myfitnesspal object"""
        food = MFPFood.identical_food(f)
        if not food:
            tot = f.totals
            food = MFPFood(name=f.name, **tot)
            db.session.add(food)
            db.session.commit()
        return food


class MFPDay(db.Model):
    """ Model to hold a day worth of myfitnesspal food data """
    __tablename__ = 'mfpday'
    date = db.Column(db.Date, primary_key=True)
    foods = db.relationship(MFPFood, secondary=foods_tbl)
    calories = db.Column(db.Integer)
    carbohydrates = db.Column(db.Integer)
    fat = db.Column(db.Integer)
    protein = db.Column(db.Integer)
    sodium = db.Column(db.Integer)
    sugar = db.Column(db.Integer)

    def food_counts(self):
        """
        Counts references to a specific food during the MFPDay. Necessary
        because Flask-SQLAlchemy / Flask-Restless only return one instance
        of each food, regardless of actual count.
        """
        counts = defaultdict(int)
        for f in set(self.foods):
            counts[f.id] = db.session.query(foods_tbl).filter_by(
                                food_id=f.id, day_date=self.date
                                ).count()
        return counts

    @staticmethod
    def save_or_update_day(d):
        """
        Saves a python-myfitnespal day object as a MFPDay in the database.
        Overrides any prefious day data for that date if it exists.
        """
        day = (MFPDay.query.filter(MFPDay.date == d.date).first() or
               MFPDay(date=d.date))
        for k in d.totals.keys():
            setattr(day, k, d.totals[k])
        foods = (food for meal in d.meals for food in meal)
        food_objs = map(MFPFood.save_food, foods)
        map(day.foods.append, food_objs)
        db.session.add(day)
        db.session.commit()


class MyFitnessPalTracker(BoleroTracker):
    service_name = 'myfitnesspal'

    @requires('myfitnesspal.username')
    def handle_authentication(self, config):
        return myfitnesspal.Client(config['myfitnesspal.username'])

    def get_day(self, date=date.today()):
        """ Saves a day's (defaults to today) nutrition entries """
        api = self.client
        day = api.get_date(date)
        MFPDay.save_or_update_day(day)

    def scrape_range(self, start, end=date.today()):
        """ Saves the range of day entries between 'start' and 'end' """
        d = start
        while d <= end:
            self.get_day(d)
            d += timedelta(days=1)

    def update(self):
        self.get_last_week()

    def backfill(self):
        # TODO: Actually find user's earliest entry; range select based on that
        self.scrape_range(date.today() - timedelta(days=365))

    def get_last_week(self):
        """ Saves the past 7 days worth of entries """
        self.scrape_range(date.today() - timedelta(days=7))

    def create_api(self, manager):
        manager.create_api(MFPDay, include_methods=['food_counts'])
