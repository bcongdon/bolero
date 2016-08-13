import json
import os

def config_file_location():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(curr_dir, os.pardir, 'config.json'))


def get_config_keys(keys):
    with open(config_file_location()) as f:
        all_keys = json.load(f)
    requested_keys = {x: all_keys[x] for x in keys}
    return requested_keys


class requires(object):
    """ Decorator to pass necessary config variables to tracker. """
    def __init__(self, *required_keys):
        self.required_keys = required_keys

    def __call__(self, func):
        def decorator():
            keys = get_config_keys(self.required_keys)
            return func(keys)
        # Preserve original function name
        decorator.__name__ = func.__name__
        decorator.__module__ = func.__module__
        return decorator
