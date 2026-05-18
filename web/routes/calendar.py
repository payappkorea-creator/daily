from flask import Blueprint, request, jsonify, render_template, current_app
from datetime import datetime, timedelta

calendar_bp = Blueprint("calendar", __name__)

STATUS_COLORS = {
    "예정": "#0d6efd",
    "진행중": "#fd7e14",
    "완료": "#198754",
    "취소": "#6c757d",
}


def to_fc_event(s):
    start_dt = f"{s['date']}T{s['time']}:00"
    end_dt = (datetime.fromisoformat(start_dt) + timedelta(hours=2)).isoformat()
    return {
        "id": s["id"],
        "title": f"[{s['region']}] {s['location']}",
        "start": start_dt,
        "end": end_dt,
        "color": STATUS_COLORS.get(s["status"], "#6c757d"),
        "extendedProps": {
            "region": s["region"],
            "status": s["status"],
            "registered": s["registered"],
            "capacity": s["capacity"],
            "services": s["services"],
            "bus_number": s["bus_number"],
        },
    }


@calendar_bp.route("/calendar")
def calendar_page():
    return render_template("calendar.html")


@calendar_bp.route("/api/calendar/events")
def calendar_events():
    manager = current_app.config["SCHEDULE_MANAGER"]
    start = request.args.get("start", "")[:10] or None
    end = request.args.get("end", "")[:10] or None

    result = manager.search_schedules(start_date=start, end_date=end)
    events = [to_fc_event(s) for s in result["schedules"]]
    return jsonify(events)
