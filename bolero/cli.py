from .app import app, setup
from .scheduler import do_all_jobs_now
from withings import WithingsAuth
import uuid


@app.cli.command()
def auth_withings():
    consumer_key = input("Consumer key?").strip()
    consumer_secret = input("Consumer secret?").strip()
    auth = WithingsAuth(consumer_key, consumer_secret)
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
def populatedb():
    setup()
    do_all_jobs_now()
