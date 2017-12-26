from .app import app, load_trackers, setup_db
from nokia import NokiaAuth
import uuid
import click
from . import tracker_classes


@app.cli.command()
def auth_nokia_health():
    consumer_key = input("Consumer key?").strip()
    consumer_secret = input("Consumer secret?").strip()
    auth = NokiaAuth(consumer_key, consumer_secret)
    authorize_url = auth.get_authorize_url()
    print("Go to %s allow the app and copy your oauth_verifier" %
          authorize_url)

    oauth_verifier = raw_input('Please enter your oauth_verifier: ')
    creds = auth.get_credentials(oauth_verifier)

    for key, val in creds.__dict__.iteritems():
        print('"{}: {}"'.format('withings.' + key, val))


@app.cli.command()
def generatesecret():
    print("Random secret: " + str(uuid.uuid4()).replace('-', ''))


@app.cli.command()
@click.option('--tracker', type=click.Choice(map(lambda x: x.service_name,
                                                 tracker_classes)))
def update(tracker):
    setup_db()
    for t in load_trackers():
        if not tracker or t.service_name == tracker:
            t().update()


@app.cli.command()
@click.option('--tracker', type=click.Choice(map(lambda x: x.service_name,
                                                 tracker_classes)))
def backfill(tracker):
    setup_db()
    for t in load_trackers():
        if not tracker or t.service_name == tracker:
            t().backfill()
