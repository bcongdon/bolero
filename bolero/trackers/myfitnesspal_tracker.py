import myfitnesspal
from ..utils import requires
from .. import db, manager
from datetime import date, timedelta
from ..scheduler import scheduler


@requires('myfitnesspal.username')
def handle_authentication(config):
    return myfitnesspal.Client(config['myfitnesspal.username'])


foods_tbl = db.Table('food_join',
                     db.Column('food_id', db.Integer,
                               db.ForeignKey('mfpfood.id')),
                     db.Column('day_date', db.Date,
                               db.ForeignKey('mfpday.date')),
                     db.Column('id', db.Integer, primary_key=True)
                     )


class MFPFood(db.Model):
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
        food_q = MFPFood.query.filter(MFPFood.name == f.name)
        if not food_q.first():
            return False
        for potential in food_q:
            if (all(f.totals[key] == getattr(potential, key)
                    for key in f.totals)):
                return potential

    @staticmethod
    def save_food(f):
        food = MFPFood.identical_food(f)
        if not food:
            tot = f.totals
            food = MFPFood(name=f.name, **tot)
            db.session.add(food)
            db.session.commit()
        return food


class MFPDay(db.Model):
    __tablename__ = 'mfpday'
    date = db.Column(db.Date, primary_key=True)
    foods = db.relationship(MFPFood, secondary=foods_tbl)
    calories = db.Column(db.Integer)
    carbohydrates = db.Column(db.Integer)
    fat = db.Column(db.Integer)
    protein = db.Column(db.Integer)
    sodium = db.Column(db.Integer)
    sugar = db.Column(db.Integer)

    @staticmethod
    def save_or_update_day(d):
        day = (MFPDay.query.filter(MFPDay.date == d.date).first() or
               MFPDay(date=d.date))
        for k in d.totals.keys():
            setattr(day, k, d.totals[k])
        foods = (food for meal in d.meals for food in meal)
        food_objs = map(MFPFood.save_food, foods)
        map(day.foods.append, food_objs)
        db.session.add(day)
        db.session.commit()


manager.create_api(MFPDay)


def get_day(date=date.today()):
    api = handle_authentication()
    day = api.get_date(date)
    MFPDay.save_or_update_day(day)


def backfill(start, end=date.today()):
    d = start
    while d <= end:
        get_day(d)
        d += timedelta(days=1)


@scheduler.scheduled_job('interval', days=1)
def get_last_week():
    backfill(date.today() - timedelta(days=7))