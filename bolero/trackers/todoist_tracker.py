from pytodoist import todoist
from . import db
import logging
from .tracker import BoleroTracker
from ..utils import requires
from dateutil.parser import parse
logger = logging.getLogger(__name__)


class TodoistTask(db.Model):
    '''
    Model to hold one instance of a Task.
        NOTE: Not primary key'd on task_id because each task can be completed
        multiple times, and repeats of a Task are issued the same task id
    '''
    id = db.Column(db.BigInteger, primary_key=True)
    task_id = db.Column(db.BigInteger)
    content = db.Column(db.Text())
    date_added = db.Column(db.DateTime(timezone=True))
    date_completed = db.Column(db.DateTime(timezone=True))
    project_id = db.Column(db.BigInteger, db.ForeignKey('todoist_project.id'))

    @staticmethod
    def save_or_update(t):
        '''
        Does an "upsert" on tasks, uses task_id, date_added and date_completed
        as tests for existance / uniqueness
        '''
        # logger.info(
        #     "Updating task: {}\t({})".format(
        #         t.id,
        #         t.content, # need to fix ascii
        #     )
        # )
        date_added, date_completed = None, None

        try:
            if t.completed_date:
                date_completed = parse(t.completed_date)
        except AttributeError:
            pass

        try:
            if t.date_added:
                date_added = parse(t.date_added)
        except AttributeError:
            pass

        task = TodoistTask.query.filter(
            (TodoistTask.task_id == t.id) &
            (TodoistTask.date_added == date_added) &
            (TodoistTask.date_completed == date_completed)
        ).first()

        if not task:
            task = TodoistTask(task_id=t.id)

        task.content = t.content
        task.project_id = t.project.id
        task.date_added = date_added
        task.date_completed = date_completed

        db.session.add(task)
        db.session.commit()


class TodoistProject(db.Model):
    '''
    Model to hold a Todoist Project (list)
    '''
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    tasks = db.relationship('TodoistTask', backref='list',
                            lazy='dynamic')

    @staticmethod
    def save_or_update(p):
        logger.info("Updating project: {}".format(p.name))

        project = TodoistProject.query.filter(
            TodoistProject.id == p.id
        ).first()

        if not project:
            project = TodoistProject(id=p.id)

        project.name = p.name
        db.session.add(project)
        db.session.commit()


class TodoistTracker(BoleroTracker):
    service_name = 'todoist'

    @requires('todoist.username', 'todoist.password')
    def handle_authentication(self, config):
        user = todoist.login(
            config['todoist.username'],
            config['todoist.password']
        )
        return user

    def update(self):
        '''
        Fetches and saves all tasks / projects of the given Todoist user
        '''

        # Save projects
        logger.info("Saving projects")
        projects = self.client.get_projects()
        for p in (projects +
                  self.client.get_archived_projects()):
            TodoistProject.save_or_update(p)

        # Save uncompleted (still pending) tasks
        logger.info("Saving pending tasks")
        for task in self.client.get_uncompleted_tasks():
            TodoistTask.save_or_update(task)

        # Save completed tasks
        logger.info("Saving completed tasks")
        for task in self.client.get_completed_tasks():
            TodoistTask.save_or_update(task)

    def create_api(self, manager):
        manager.create_api(TodoistTask)
        manager.create_api(TodoistProject)
