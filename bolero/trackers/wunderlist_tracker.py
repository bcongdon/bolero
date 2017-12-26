import wunderpy2
from . import db
from ..utils import requires
from .tracker import BoleroTracker
import logging
from dateutil.parser import parse
from itertools import chain
logger = logging.getLogger(__name__)


class WunderlistTask(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True))
    completed_at = db.Column(db.DateTime(timezone=True))
    list_id = db.Column(db.BigInteger, db.ForeignKey('wunderlist_list.id'))

    @staticmethod
    def save_or_update(t):
        task = (WunderlistTask.query.filter(
                    WunderlistTask.id == t['id']).first() or
                WunderlistTask(id=t['id']))
        task.title = t['title']
        task.created_at = parse(t['created_at'])
        task.list_id = t['list_id']
        if t['completed']:
            task.completed_at = parse(t['completed_at'])
        db.session.add(task)
        db.session.commit()


class WunderlistList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True))
    public = db.Column(db.Boolean)
    tasks = db.relationship('WunderlistTask', backref='list',
                            lazy='dynamic')

    @staticmethod
    def save_or_update(l):
        _list = (WunderlistList.query.filter(
                    WunderlistList.id == l['id']).first() or
                 WunderlistList(id=l['id']))
        _list.title = l['title']
        _list.created_at = l['created_at']
        _list.public = l['public']
        db.session.add(_list)
        db.session.commit()


class WunderlistTracker(BoleroTracker):
    service_name = 'wunderlist'

    @requires('wunderlist.access_token', 'wunderlist.client_id')
    def handle_authentication(self, config):
        api = wunderpy2.WunderApi()
        client = api.get_client(config['wunderlist.access_token'],
                                config['wunderlist.client_id'])
        return client

    def update(self):
        self.get_tasks()

    def get_tasks(self):
        """
        Syncs and saves all completed and non-completed tasks for the
        authenticated user
        """
        api = self.client
        lists = api.get_lists()
        map(WunderlistList.save_or_update, lists)
        list_ids = map(lambda x: x['id'], lists)
        uncompleted = (api.get_tasks(_id) for _id in list_ids)
        completed = (api.get_tasks(_id, completed=True) for _id in list_ids)
        total = (i for sublist in chain(uncompleted, completed)
                 for i in sublist)
        map(WunderlistTask.save_or_update, total)

    def create_api(self, manager):
        manager.create_api(WunderlistTask, methods=['GET'])
