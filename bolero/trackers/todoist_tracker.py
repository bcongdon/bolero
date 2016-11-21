import todoist
from . import db
import logging
from .tracker import BoleroTracker
from ..utils import requires
logger = logging.getLogger(__name__)


class TodoistTask(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True))
    completed_at = db.Column(db.DateTime(timezone=True))
    list_id = db.Column(db.BigInteger, db.ForeignKey('list.id'))


class TodoistTracker(BoleroTracker):
    service_name = 'todoist'

    @requires('todoist.username', 'todoist.password')
    def handle_authentication(self, config):
        api = todoist.TodoistAPI()
        return api.user.login(config['todoist.username'],
                              config['todoist.password'])

    def update(self):
        response = self.client.sync()

