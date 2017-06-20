from apscheduler.schedulers.background import BackgroundScheduler
import logging
logger = logging.getLogger(__file__)

executors = {
    'default': {'type': 'threadpool', 'max_workers': 20},
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

scheduler = BackgroundScheduler()

def initialize_scheduler():
    # Setup and start scheduler
    scheduler.configure(executors=executors,
                        job_defaults=job_defaults)
    logger.info('Starting scheduler')
    scheduler.start()
