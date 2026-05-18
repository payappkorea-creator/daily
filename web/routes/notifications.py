from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("/api/notifications/upcoming")
def upcoming_notifications():
    manager = current_app.config["SCHEDULE_MANAGER"]
    days = request.args.get("days", 7, type=int)
    result = manager.get_upcoming_schedules(days=days)
    result["checked_at"] = datetime.now().isoformat(timespec="seconds")
    return jsonify(result)
