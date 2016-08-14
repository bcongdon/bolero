import wunderpy2
from .. import db, manager
from ..utils import requires
from ..scheduler import scheduler
import logging
from dateutil.parser import parse
from itertools import chain
logger = logging.getLogger(__name__)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer)
    title = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True))
    completed_at = db.Column(db.DateTime(timezone=True))


@requires('wunderlist.access_token', 'wunderlist.client_id')
def handle_authentication(config):
    api = wunderpy2.WunderApi()
    client = api.get_client(config['wunderlist.access_token'],
                            config['wunderlist.client_id'])
    return client


def save_or_update(t):
    task = Task.query.filter(Task.id == t['id']).first() or Task(id=t['id'])
    task.list_id = t['list_id']
    task.title = t['title']
    task.created_at = parse(t['created_at'])
    if t['completed']:
        task.completed_at = parse(t['completed_at'])

    db.session.add(task)
    db.session.commit()


@scheduler.scheduled_job('interval', hours=1)
def get_tasks():
    api = handle_authentication()
    list_ids = map(lambda x: x['id'], api.get_lists())
    uncompleted = (api.get_tasks(_id) for _id in list_ids)
    completed = (api.get_tasks(_id, completed=True) for _id in list_ids)
    total = (i for sublist in chain(uncompleted, completed)
             for i in sublist)
    map(save_or_update, total)

manager.create_api(Task, methods=['GET', 'POST'])
