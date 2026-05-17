import json
import os
from datetime import datetime, date, timedelta

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "schedules.json")

VALID_STATUSES = {"예정", "진행중", "완료", "취소"}
VALID_REGIONS = {
    "목포시", "여수시", "순천시", "나주시", "광양시",
    "담양군", "곡성군", "구례군", "고흥군", "보성군",
    "화순군", "장흥군", "강진군", "해남군", "영암군",
    "무안군", "함평군", "영광군", "장성군", "완도군",
    "진도군", "신안군",
}


class ScheduleManager:
    def __init__(self):
        self._ensure_data_file()

    def _ensure_data_file(self):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        if not os.path.exists(DATA_FILE):
            self._save({"schedules": [], "last_id": 0})

    def _load(self) -> dict:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: dict):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def search_schedules(
        self,
        start_date: str = None,
        end_date: str = None,
        region: str = None,
        status: str = None,
    ) -> dict:
        data = self._load()
        results = data["schedules"]

        if start_date:
            results = [s for s in results if s["date"] >= start_date]
        if end_date:
            results = [s for s in results if s["date"] <= end_date]
        if region:
            results = [s for s in results if s["region"] == region]
        if status:
            results = [s for s in results if s["status"] == status]

        results = sorted(results, key=lambda s: (s["date"], s["time"]))
        return {"count": len(results), "schedules": results}

    def get_schedule(self, schedule_id: str) -> dict:
        data = self._load()
        for s in data["schedules"]:
            if s["id"] == schedule_id:
                return {"success": True, "schedule": s}
        return {"success": False, "error": f"일정 ID '{schedule_id}'를 찾을 수 없습니다."}

    def add_schedule(
        self,
        date: str,
        region: str,
        location: str,
        time: str = "10:00",
        address: str = "",
        services: list = None,
        staff: list = None,
        capacity: int = 50,
        bus_number: str = "행복버스 1호",
        contact: str = "",
        notes: str = "",
    ) -> dict:
        if region not in VALID_REGIONS:
            return {"success": False, "error": f"'{region}'은 전남 22개 시군에 포함되지 않습니다."}

        data = self._load()
        new_id_num = data.get("last_id", 0) + 1
        new_id = f"SCH-{new_id_num:03d}"

        schedule = {
            "id": new_id,
            "date": date,
            "time": time,
            "region": region,
            "location": location,
            "address": address,
            "services": services or [],
            "staff": staff or [],
            "capacity": capacity,
            "registered": 0,
            "bus_number": bus_number,
            "status": "예정",
            "contact": contact,
            "notes": notes,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }

        data["schedules"].append(schedule)
        data["last_id"] = new_id_num
        self._save(data)
        return {"success": True, "schedule": schedule}

    def update_schedule(self, schedule_id: str, **kwargs) -> dict:
        data = self._load()
        for i, s in enumerate(data["schedules"]):
            if s["id"] == schedule_id:
                if "status" in kwargs and kwargs["status"] not in VALID_STATUSES:
                    return {
                        "success": False,
                        "error": f"유효하지 않은 상태값입니다. 허용값: {', '.join(VALID_STATUSES)}",
                    }
                if "region" in kwargs and kwargs["region"] not in VALID_REGIONS:
                    return {
                        "success": False,
                        "error": f"'{kwargs['region']}'은 전남 22개 시군에 포함되지 않습니다.",
                    }
                updatable = {
                    "date", "time", "region", "location", "address",
                    "services", "staff", "capacity", "registered",
                    "bus_number", "status", "contact", "notes",
                }
                for key, value in kwargs.items():
                    if key in updatable:
                        data["schedules"][i][key] = value
                self._save(data)
                return {"success": True, "schedule": data["schedules"][i]}
        return {"success": False, "error": f"일정 ID '{schedule_id}'를 찾을 수 없습니다."}

    def delete_schedule(self, schedule_id: str) -> dict:
        data = self._load()
        for i, s in enumerate(data["schedules"]):
            if s["id"] == schedule_id:
                removed = data["schedules"].pop(i)
                self._save(data)
                return {"success": True, "deleted_schedule": removed}
        return {"success": False, "error": f"일정 ID '{schedule_id}'를 찾을 수 없습니다."}

    def get_upcoming_schedules(self, days: int = 30, region: str = None) -> dict:
        today = datetime.now().date().isoformat()
        end = (datetime.now().date() + timedelta(days=days)).isoformat()
        result = self.search_schedules(start_date=today, end_date=end, region=region, status="예정")
        return result

    def get_statistics(self, year: int = None, month: int = None) -> dict:
        data = self._load()
        schedules = data["schedules"]

        if year:
            schedules = [s for s in schedules if s["date"].startswith(str(year))]
        if month:
            month_str = f"{year or datetime.now().year}-{month:02d}"
            schedules = [s for s in schedules if s["date"].startswith(month_str)]

        status_counts = {}
        region_counts = {}
        total_capacity = 0
        total_registered = 0

        for s in schedules:
            status_counts[s["status"]] = status_counts.get(s["status"], 0) + 1
            region_counts[s["region"]] = region_counts.get(s["region"], 0) + 1
            total_capacity += s.get("capacity", 0)
            total_registered += s.get("registered", 0)

        utilization = (
            round(total_registered / total_capacity * 100, 1) if total_capacity > 0 else 0
        )

        return {
            "total_schedules": len(schedules),
            "status_breakdown": status_counts,
            "region_breakdown": region_counts,
            "total_capacity": total_capacity,
            "total_registered": total_registered,
            "utilization_rate": f"{utilization}%",
        }
