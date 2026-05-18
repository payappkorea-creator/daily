from flask import Blueprint, request, jsonify, render_template, redirect, url_for, current_app

schedules_bp = Blueprint("schedules", __name__)


def get_manager():
    return current_app.config["SCHEDULE_MANAGER"]


# ── HTML 페이지 라우트 ──────────────────────────────────────────────────────────

@schedules_bp.route("/schedules")
def list_schedules():
    manager = get_manager()
    region = request.args.get("region", "")
    status = request.args.get("status", "")
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")

    result = manager.search_schedules(
        start_date=start_date or None,
        end_date=end_date or None,
        region=region or None,
        status=status or None,
    )
    return render_template(
        "schedules/list.html",
        schedules=result["schedules"],
        count=result["count"],
        filters={"region": region, "status": status, "start_date": start_date, "end_date": end_date},
    )


@schedules_bp.route("/schedules/new")
def new_schedule():
    return render_template("schedules/form.html", schedule=None)


@schedules_bp.route("/schedules/<schedule_id>")
def detail_schedule(schedule_id):
    manager = get_manager()
    result = manager.get_schedule(schedule_id)
    if not result["success"]:
        return render_template("schedules/list.html", error=result["error"], schedules=[], count=0, filters={}), 404
    return render_template("schedules/detail.html", schedule=result["schedule"])


@schedules_bp.route("/schedules/<schedule_id>/edit")
def edit_schedule(schedule_id):
    manager = get_manager()
    result = manager.get_schedule(schedule_id)
    if not result["success"]:
        return redirect(url_for("schedules.list_schedules"))
    return render_template("schedules/form.html", schedule=result["schedule"])


# ── JSON API 라우트 ────────────────────────────────────────────────────────────

@schedules_bp.route("/api/schedules", methods=["GET"])
def api_list_schedules():
    manager = get_manager()
    result = manager.search_schedules(
        start_date=request.args.get("start_date"),
        end_date=request.args.get("end_date"),
        region=request.args.get("region"),
        status=request.args.get("status"),
    )
    return jsonify(result)


@schedules_bp.route("/api/schedules", methods=["POST"])
def api_create_schedule():
    manager = get_manager()
    data = request.get_json(force=True)
    if not data:
        return jsonify({"success": False, "error": "요청 데이터가 없습니다."}), 400

    result = manager.add_schedule(
        date=data.get("date", ""),
        region=data.get("region", ""),
        location=data.get("location", ""),
        time=data.get("time", "10:00"),
        address=data.get("address", ""),
        services=data.get("services", []),
        staff=data.get("staff", []),
        capacity=int(data.get("capacity", 50)),
        bus_number=data.get("bus_number", "행복버스 1호"),
        contact=data.get("contact", ""),
        notes=data.get("notes", ""),
    )
    if result["success"]:
        return jsonify(result), 201
    return jsonify(result), 400


@schedules_bp.route("/api/schedules/<schedule_id>", methods=["GET"])
def api_get_schedule(schedule_id):
    manager = get_manager()
    result = manager.get_schedule(schedule_id)
    if not result["success"]:
        return jsonify(result), 404
    return jsonify(result)


@schedules_bp.route("/api/schedules/<schedule_id>", methods=["PUT"])
def api_update_schedule(schedule_id):
    manager = get_manager()
    data = request.get_json(force=True) or {}
    if "capacity" in data:
        data["capacity"] = int(data["capacity"])
    if "registered" in data:
        data["registered"] = int(data["registered"])
    result = manager.update_schedule(schedule_id, **data)
    if not result["success"]:
        return jsonify(result), 400
    return jsonify(result)


@schedules_bp.route("/api/schedules/<schedule_id>", methods=["DELETE"])
def api_delete_schedule(schedule_id):
    manager = get_manager()
    result = manager.delete_schedule(schedule_id)
    if not result["success"]:
        return jsonify(result), 404
    return jsonify(result)


# ── 폼 제출 처리 (HTML form POST) ─────────────────────────────────────────────

@schedules_bp.route("/schedules", methods=["POST"])
def create_schedule():
    manager = get_manager()
    staff_raw = request.form.getlist("staff")
    staff = [s.strip() for s in staff_raw if s.strip()]

    result = manager.add_schedule(
        date=request.form.get("date", ""),
        region=request.form.get("region", ""),
        location=request.form.get("location", ""),
        time=request.form.get("time", "10:00"),
        address=request.form.get("address", ""),
        services=request.form.getlist("services"),
        staff=staff,
        capacity=int(request.form.get("capacity", 50)),
        bus_number=request.form.get("bus_number", "행복버스 1호"),
        contact=request.form.get("contact", ""),
        notes=request.form.get("notes", ""),
    )
    if result["success"]:
        return redirect(url_for("schedules.detail_schedule", schedule_id=result["schedule"]["id"]))
    return render_template("schedules/form.html", schedule=None, error=result["error"])


@schedules_bp.route("/schedules/<schedule_id>/edit", methods=["POST"])
def update_schedule(schedule_id):
    manager = get_manager()
    staff_raw = request.form.getlist("staff")
    staff = [s.strip() for s in staff_raw if s.strip()]

    result = manager.update_schedule(
        schedule_id,
        date=request.form.get("date"),
        region=request.form.get("region"),
        location=request.form.get("location"),
        time=request.form.get("time"),
        address=request.form.get("address"),
        services=request.form.getlist("services"),
        staff=staff,
        capacity=int(request.form.get("capacity", 50)),
        registered=int(request.form.get("registered", 0)),
        bus_number=request.form.get("bus_number"),
        status=request.form.get("status"),
        contact=request.form.get("contact"),
        notes=request.form.get("notes"),
    )
    if result["success"]:
        return redirect(url_for("schedules.detail_schedule", schedule_id=schedule_id))
    existing = manager.get_schedule(schedule_id)
    return render_template(
        "schedules/form.html",
        schedule=existing.get("schedule"),
        error=result["error"],
    )


@schedules_bp.route("/schedules/<schedule_id>/delete", methods=["POST"])
def delete_schedule(schedule_id):
    manager = get_manager()
    manager.delete_schedule(schedule_id)
    return redirect(url_for("schedules.list_schedules"))
