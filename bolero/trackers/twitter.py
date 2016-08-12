from .. import app, db
from datetime import datetime


class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    published_at = db.Column(db.DateTime, default=datetime.now)
    user = db.Column(db.String(80))
    likes = db.Column(db.Integer, default=0)
    retweets = db.Column(db.Integer, default=0)
