from .. import db
from datetime import datetime, timedelta
from ..utils import requires
import tweepy
import logging
logger = logging.getLogger(__name__)

class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    user = db.Column(db.String(80))
    favorites = db.Column(db.Integer, default=0)
    retweets = db.Column(db.Integer, default=0)


@requires('twitter.consumer_key', 'twitter.consumer_secret',
          'twitter.access_token_key', 'twitter.access_token_secret')
def handle_authentication(config):
    auth = tweepy.OAuthHandler(config['twitter.consumer_key'],
                               config['twitter.consumer_secret'])
    auth.set_access_token(config['twitter.access_token_key'],
                          config['twitter.access_token_secret'])
    return tweepy.API(auth)


def get_tweets():
    def within_one_day(time):
        return datetime.utcnow() - time < timedelta(1)

    api = handle_authentication()
    page = 0
    while True:
        tweet_page = api.user_timeline(count=100, page=page)
        tweet_ids = map(lambda t: t.id, tweet_page)
        saved_ids = map(lambda t: t.id, Tweet.query.filter(Tweet.id.in_(tweet_ids)))
        unsaved = filter(lambda t: t.id not in saved_ids, tweet_page)
        for t in unsaved:
            new_tweet = Tweet(id=t.id,
                              text=t.text,
                              user=t.user.screen_name,
                              favorites=t.favorite_count,
                              retweets=t.retweet_count,
                              created_at=t.created_at)
            db.session.add(new_tweet)
        db.session.commit()
        return
