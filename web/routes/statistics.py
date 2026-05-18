from flask import Blueprint, request, jsonify, render_template, current_app
from datetime import datetime

statistics_bp = Blueprint("statistics", __name__)


@statistics_bp.route("/statistics")
def statistics_page():
    manager = current_app.config["SCHEDULE_MANAGER"]
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)

    stats = manager.get_statistics(year=year, month=month)
    current_year = datetime.now().year
    years = list(range(current_year - 1, current_year + 2))

    return render_template(
        "statistics.html",
        stats=stats,
        selected_year=year or "",
        selected_month=month or "",
        years=years,
    )


@statistics_bp.route("/api/statistics")
def api_statistics():
    manager = current_app.config["SCHEDULE_MANAGER"]
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    return jsonify(manager.get_statistics(year=year, month=month))
