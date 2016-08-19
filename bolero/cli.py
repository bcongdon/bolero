from . import app
from withings import WithingsAuth


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
