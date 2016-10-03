class BoleroTracker(object):
    def __init__(self):
        self.client = self.handleAuthentication()

    def handleAuthentication(self):
        raise NotImplementedError

    def backfill(self):
        raise NotImplementedError

    def create_api(self, manager):
        raise NotImplementedError
