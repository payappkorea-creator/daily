import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template
from schedule_manager import ScheduleManager, VALID_REGIONS, VALID_STATUSES

from routes.schedules import schedules_bp
from routes.calendar import calendar_bp
from routes.statistics import statistics_bp
from routes.notifications import notifications_bp

app = Flask(__name__)
app.secret_key = "happybus-secret-2026"

manager = ScheduleManager()
app.config["SCHEDULE_MANAGER"] = manager

app.register_blueprint(schedules_bp)
app.register_blueprint(calendar_bp)
app.register_blueprint(statistics_bp)
app.register_blueprint(notifications_bp)


@app.context_processor
def inject_globals():
    return {
        "VALID_REGIONS": sorted(VALID_REGIONS),
        "VALID_STATUSES": list(VALID_STATUSES),
        "SERVICES_LIST": ["복지상담", "의료서비스", "법률상담", "행정서비스", "건강검진"],
    }


@app.route("/")
def index():
    upcoming = manager.get_upcoming_schedules(days=30)
    stats = manager.get_statistics()
    return render_template("index.html", upcoming=upcoming["schedules"], stats=stats)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
