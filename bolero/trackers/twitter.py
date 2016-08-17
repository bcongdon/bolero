from .. import db, manager
from datetime import datetime
from ..utils import requires
from ..scheduler import scheduler
import tweepy
import logging
logger = logging.getLogger(__name__)


class Tweet(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    user = db.Column(db.String(80))
    favorites = db.Column(db.Integer, default=0)
    retweets = db.Column(db.Integer, default=0)


class FollowerCount(db.Model):
    __tablename__ = "twitterfollowercount"
    date = db.Column(db.DateTime(timezone=True), default=datetime.now,
                     primary_key=True)
    count = db.Column(db.Integer)


@requires('twitter.consumer_key', 'twitter.consumer_secret',
          'twitter.access_token_key', 'twitter.access_token_secret')
def handle_authentication(config):
    auth = tweepy.OAuthHandler(config['twitter.consumer_key'],
                               config['twitter.consumer_secret'])
    auth.set_access_token(config['twitter.access_token_key'],
                          config['twitter.access_token_secret'])
    return tweepy.API(auth)


def save_tweet(t):
    new_tweet = Tweet(id=t.id,
                      text=t.text,
                      user=t.user.screen_name,
                      favorites=t.favorite_count,
                      retweets=t.retweet_count,
                      created_at=t.created_at)
    db.session.add(new_tweet)
    db.session.commit()


@scheduler.scheduled_job('interval', hours=1)
def get_tweets():
    """
    Saves all tweets sent by authenticated user until it finds tweets that have
    already been saved.
    """
    api = handle_authentication()
    page = 1
    while True:
        logger.info("Scraping page {0} of tweets.".format(page))
        tweet_page = api.user_timeline(count=100, page=page)
        tweet_ids = map(lambda t: t.id, tweet_page)
        saved_ids = map(lambda t: t.id,
                        Tweet.query.filter(Tweet.id.in_(tweet_ids)))
        unsaved = filter(lambda t: t.id not in saved_ids, tweet_page)
        if len(unsaved) > 0:
            page += 1
            map(save_tweet, unsaved)
            logger.info("Saved {0} tweets.".format(len(unsaved)))
        else:
            return


@scheduler.scheduled_job('interval', hours=12)
def get_followers():
    """ Saves authenticated user's current number of followers """
    api = handle_authentication()
    count = api.me().followers_count
    f = FollowerCount(date=datetime.now(), count=count)
    db.session.add(f)
    db.session.commit()
    logger.info("Saved follower count: {0}".format(count))

manager.create_api(Tweet,  methods=['GET'])
