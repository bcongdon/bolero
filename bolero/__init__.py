from .trackers.fitbit_tracker import FitbitTracker
from .trackers.myfitnesspal_tracker import MyFitnessPalTracker
from .trackers.nokia_health_tracker import NokiaHealthTracker
from .trackers.todoist_tracker import TodoistTracker
from .trackers.twitter_tracker import TwitterTracker
from .trackers.wunderlist_tracker import WunderlistTracker

tracker_classes = [
    FitbitTracker,
    MyFitnessPalTracker,
    NokiaHealthTracker,
    TodoistTracker,
    TwitterTracker,
    WunderlistTracker,
]
