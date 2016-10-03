from ..app import manager
from . import db
from datetime import datetime
from ..utils import requires, check_auth, get_or_create
from ..scheduler import scheduler
from .tracker import BoleroTracker
import tweepy
import logging
logger = logging.getLogger(__name__)


class Tweet(db.Model):
    """ Model to hold a single tweet """
    id = db.Column(db.BigInteger, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    user = db.Column(db.String(80))
    favorites = db.Column(db.Integer, default=0)
    retweets = db.Column(db.Integer, default=0)


class FollowerCount(db.Model):
    """ Model to hold a single measurement of the user's follower count """
    __tablename__ = "twitterfollowercount"
    date = db.Column(db.DateTime(timezone=True), default=datetime.now,
                     primary_key=True)
    count = db.Column(db.Integer)


class TwitterTracker(BoleroTracker):
    @requires('twitter.consumer_key', 'twitter.consumer_secret',
              'twitter.access_token_key', 'twitter.access_token_secret')
    def handle_authentication(self, config):
        """ Authenticate and return an authenticated tweepy API object """
        auth = tweepy.OAuthHandler(config['twitter.consumer_key'],
                                   config['twitter.consumer_secret'])
        auth.set_access_token(config['twitter.access_token_key'],
                              config['twitter.access_token_secret'])
        return tweepy.API(auth)

    def save_tweet(self, t):
        """ Saves a tweepy tweet object as a Tweet in the database """
        new_tweet = get_or_create(db.session, Tweet,
                                  id=t.id,
                                  text=t.text,
                                  user=t.user.screen_name,
                                  created_at=t.created_at)
        new_tweet.favorites = t.favorite_count
        new_tweet.retweets = t.retweet_count
        db.session.add(new_tweet)
        db.session.commit()

    # @scheduler.scheduled_job('interval', hours=1)
    def get_tweets(self, backfill=True):
        """
        Grabs and saves all tweets sent by authenticated user until it finds
        tweets that have already been saved.
        """
        api = self.client
        page = 1
        while True:
            logger.info("Scraping page {0} of tweets.".format(page))
            tweet_page = api.user_timeline(count=100, page=page)

            # Get list of tweet_ids
            tweet_ids = map(lambda t: t.id, tweet_page)

            # Get list of tweet_ids saved in the DB
            saved_ids = map(lambda t: t.id,
                            Tweet.query.filter(Tweet.id.in_(tweet_ids)))

            # Filter out any tweets that have already been saved
            unsaved = list(filter(lambda t: t.id not in saved_ids, tweet_page))

            # Save any unsaved tweets
            if (unsaved or backfill) and tweet_page:
                page += 1
                for tweet in tweet_page:
                    self.save_tweet(tweet)
                logger.info("Saved {0} tweets.".format(len(unsaved)))
            else:
                break  # Break if there are no unsaved tweets in this page

    # @scheduler.scheduled_job('interval', hours=12)
    def get_followers(self):
        """ Saves authenticated user's current number of followers """
        api = self.client
        count = api.me().followers_count
        f = FollowerCount(date=datetime.now(), count=count)
        db.session.add(f)
        db.session.commit()
        logger.info("Saved follower count: {0}".format(count))

    def create_api():
        manager.create_api(Tweet,  preprocessors={'GET_SINGLE': [check_auth]})

    def backfill():
        self.get_tweets(backfill=True)
