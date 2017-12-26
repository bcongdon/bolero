from .trackers.fitbit_tracker import FitbitTracker
from .trackers.myfitnesspal_tracker import MyFitnessPalTracker
from .trackers.nokia_health import NokiaHealthTracker
from .trackers.todoist_tracker import TodoistTracker
from .trackers.twitter import TwitterTracker
from .trackers.wunderlist import WunderlistTracker

tracker_classes = [
    FitbitTracker,
    MyFitnessPalTracker,
    NokiaHealthTracker,
    TodoistTracker,
    TwitterTracker,
    WunderlistTracker,
]
