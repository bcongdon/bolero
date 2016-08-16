from apscheduler.schedulers.background import BackgroundScheduler

executors = {
    'default': {'type': 'threadpool', 'max_workers': 20},
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

# Setup and start scheduler
scheduler = BackgroundScheduler()
scheduler.configure(executors=executors,
                    job_defaults=job_defaults)
scheduler.start()


def do_all_jobs_now():
    jobs = scheduler.get_jobs()
    for job in jobs:
        job.func()
