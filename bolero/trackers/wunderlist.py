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
    title = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True))
    completed_at = db.Column(db.DateTime(timezone=True))
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'))

    @staticmethod
    def save_or_update(t):
        task = Task.query.filter(Task.id == t['id']).first() or Task(id=t['id'])
        task.title = t['title']
        task.created_at = parse(t['created_at'])
        task.list_id = t['list_id']
        if t['completed']:
            task.completed_at = parse(t['completed_at'])
        db.session.add(task)
        db.session.commit()


class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True))
    public = db.Column(db.Boolean)
    tasks = db.relationship('Task', backref='list',
                            lazy='dynamic')

    @staticmethod
    def save_or_update(l):
        _list = (List.query.filter(List.id == l['id']).first() or
                 List(id=l['id']))
        _list.title = l['title']
        _list.created_at = l['created_at']
        _list.public = l['public']
        db.session.add(_list)
        db.session.commit()


@requires('wunderlist.access_token', 'wunderlist.client_id')
def handle_authentication(config):
    api = wunderpy2.WunderApi()
    client = api.get_client(config['wunderlist.access_token'],
                            config['wunderlist.client_id'])
    return client


from datetime import datetime
@scheduler.scheduled_job('interval', hours=1)
def get_tasks():
    api = handle_authentication()
    lists = api.get_lists()
    map(List.save_or_update, lists)
    list_ids = map(lambda x: x['id'], lists)
    uncompleted = (api.get_tasks(_id) for _id in list_ids)
    completed = (api.get_tasks(_id, completed=True) for _id in list_ids)
    total = (i for sublist in chain(uncompleted, completed)
             for i in sublist)
    map(Task.save_or_update, total)

manager.create_api(Task, methods=['GET'])
