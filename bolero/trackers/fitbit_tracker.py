import fitbit
from ..utils import requires


@requires('fitbit.consumer_key', 'fitbit.consumer_secret',
          'fitbit.refresh_token', 'fitbit.access_token')
def handle_authentication(config):
    return fitbit.Fitbit(config['fitbit.consumer_key'],
                         config['fitbit.consumer_secret'],
                         access_token=config['fitbit.access_token'],
                         refresh_token=config['fitbit.refresh_token'])
