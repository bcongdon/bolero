from .trackers.twitter import TwitterTracker
from .trackers.myfitnesspal_tracker import MyFitnessPalTracker
from .trackers.withings_tracker import WithingsTracker
from .trackers.wunderlist import WunderlistTracker
from .trackers.todoist_tracker import TodoistTracker

tracker_classes = [
    TwitterTracker,
    MyFitnessPalTracker,
    WithingsTracker,
    WunderlistTracker,
    TodoistTracker
]
