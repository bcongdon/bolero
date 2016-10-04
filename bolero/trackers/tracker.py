class BoleroTracker(object):
    # Default APScheduler interval for 'update' scheduled scrape
    update_interval = {'hours': 1}

    # Default APScheduler interval for full 'backfill' scrape
    backfill_interval = {'days': 3}

    # Service name - used for enabling via config
    service_name = None

    def __init__(self):
        self.client = self.handle_authentication()

    def handle_authentication(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def backfill(self):
        self.update()

    def create_api(self, manager):
        raise NotImplementedError
