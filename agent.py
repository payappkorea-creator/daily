import json
import os
import anthropic
from schedule_manager import ScheduleManager

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
manager = ScheduleManager()

SYSTEM_PROMPT = """당신은 전라남도 '찾아가는 전남행복버스' 일정 관리 전담 에이전트입니다.

전남행복버스는 복지·의료·행정 서비스를 직접 찾아가 제공하는 이동형 공공서비스 버스입니다.
농어촌 도서벽지 주민들이 쉽게 받기 어려운 서비스를 현장에서 제공합니다.

전남 22개 시군: 목포시, 여수시, 순천시, 나주시, 광양시, 담양군, 곡성군, 구례군, 고흥군,
보성군, 화순군, 장흥군, 강진군, 해남군, 영암군, 무안군, 함평군, 영광군, 장성군, 완도군, 진도군, 신안군

일정 상태 유형: 예정 / 진행중 / 완료 / 취소

담당 업무:
- 방문 일정 조회, 등록, 수정, 삭제
- 다가오는 일정 안내
- 지역별·상태별 일정 검색
- 운영 통계 제공

오늘 날짜 기준으로 답변하며, 날짜 정보가 필요할 때는 오늘이 2026-05-17임을 참고하세요.
항상 친절하고 명확하게 답변하며, 도구를 적극 활용해 정확한 정보를 제공하세요."""

TOOLS = [
    {
        "name": "search_schedules",
        "description": "일정을 조건에 따라 검색합니다. 날짜 범위, 지역, 상태로 필터링할 수 있습니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "검색 시작 날짜 (YYYY-MM-DD 형식)",
                },
                "end_date": {
                    "type": "string",
                    "description": "검색 종료 날짜 (YYYY-MM-DD 형식)",
                },
                "region": {
                    "type": "string",
                    "description": "지역명 (예: 고흥군, 진도군). 전남 22개 시군 중 하나.",
                },
                "status": {
                    "type": "string",
                    "description": "일정 상태. 예정 / 진행중 / 완료 / 취소 중 하나.",
                    "enum": ["예정", "진행중", "완료", "취소"],
                },
            },
        },
    },
    {
        "name": "get_schedule",
        "description": "일정 ID로 특정 일정의 상세 정보를 조회합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "schedule_id": {
                    "type": "string",
                    "description": "조회할 일정 ID (예: SCH-001)",
                }
            },
            "required": ["schedule_id"],
        },
    },
    {
        "name": "add_schedule",
        "description": "새 방문 일정을 등록합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "방문 날짜 (YYYY-MM-DD 형식)"},
                "region": {"type": "string", "description": "방문 지역 (전남 22개 시군 중 하나)"},
                "location": {"type": "string", "description": "방문 장소명"},
                "time": {"type": "string", "description": "방문 시간 (HH:MM 형식, 기본값: 10:00)"},
                "address": {"type": "string", "description": "방문 장소 주소"},
                "services": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "제공 서비스 목록 (예: ['복지상담', '의료서비스', '법률상담', '행정서비스', '건강검진'])",
                },
                "staff": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "담당 직원 목록",
                },
                "capacity": {"type": "integer", "description": "수용 인원 (기본값: 50)"},
                "bus_number": {
                    "type": "string",
                    "description": "버스 호수 (예: 행복버스 1호, 행복버스 2호)",
                },
                "contact": {"type": "string", "description": "연락처"},
                "notes": {"type": "string", "description": "비고"},
            },
            "required": ["date", "region", "location"],
        },
    },
    {
        "name": "update_schedule",
        "description": "기존 일정을 수정합니다. 수정할 항목만 지정하면 됩니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "schedule_id": {"type": "string", "description": "수정할 일정 ID (예: SCH-006)"},
                "date": {"type": "string", "description": "변경할 날짜 (YYYY-MM-DD)"},
                "time": {"type": "string", "description": "변경할 시간 (HH:MM)"},
                "region": {"type": "string", "description": "변경할 지역"},
                "location": {"type": "string", "description": "변경할 장소명"},
                "address": {"type": "string", "description": "변경할 주소"},
                "services": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "변경할 서비스 목록",
                },
                "staff": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "변경할 담당자 목록",
                },
                "capacity": {"type": "integer", "description": "변경할 수용 인원"},
                "registered": {"type": "integer", "description": "변경할 등록 인원"},
                "bus_number": {"type": "string", "description": "변경할 버스 호수"},
                "status": {
                    "type": "string",
                    "description": "변경할 상태",
                    "enum": ["예정", "진행중", "완료", "취소"],
                },
                "contact": {"type": "string", "description": "변경할 연락처"},
                "notes": {"type": "string", "description": "변경할 비고"},
            },
            "required": ["schedule_id"],
        },
    },
    {
        "name": "delete_schedule",
        "description": "일정을 삭제합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "schedule_id": {
                    "type": "string",
                    "description": "삭제할 일정 ID (예: SCH-006)",
                }
            },
            "required": ["schedule_id"],
        },
    },
    {
        "name": "get_upcoming_schedules",
        "description": "오늘부터 지정한 기간 내의 예정된 일정을 조회합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "오늘부터 몇 일 이내의 일정을 조회할지 (기본값: 30)",
                },
                "region": {
                    "type": "string",
                    "description": "특정 지역으로 필터링할 경우 지역명",
                },
            },
        },
    },
    {
        "name": "get_statistics",
        "description": "일정 운영 통계를 조회합니다. 상태별, 지역별 현황과 수용·등록 인원 통계를 제공합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "통계 조회 연도 (예: 2026)"},
                "month": {"type": "integer", "description": "통계 조회 월 (1~12)"},
            },
        },
    },
]


def execute_tool(tool_name: str, tool_input: dict) -> str:
    try:
        if tool_name == "search_schedules":
            result = manager.search_schedules(**tool_input)
        elif tool_name == "get_schedule":
            result = manager.get_schedule(**tool_input)
        elif tool_name == "add_schedule":
            result = manager.add_schedule(**tool_input)
        elif tool_name == "update_schedule":
            kwargs = dict(tool_input)
            schedule_id = kwargs.pop("schedule_id")
            result = manager.update_schedule(schedule_id, **kwargs)
        elif tool_name == "delete_schedule":
            result = manager.delete_schedule(**tool_input)
        elif tool_name == "get_upcoming_schedules":
            result = manager.get_upcoming_schedules(**tool_input)
        elif tool_name == "get_statistics":
            result = manager.get_statistics(**tool_input)
        else:
            result = {"error": f"알 수 없는 도구: {tool_name}"}
    except Exception as e:
        result = {"error": str(e)}

    return json.dumps(result, ensure_ascii=False)


def run_agent():
    messages = []
    print("=" * 60)
    print("  찾아가는 전남행복버스 일정 관리 에이전트")
    print("=" * 60)
    print("안녕하세요! 전남행복버스 일정 관리 에이전트입니다.")
    print("일정 조회, 등록, 수정, 삭제 등 무엇이든 도와드립니다.")
    print("종료하려면 'quit' 또는 '종료'를 입력하세요.")
    print("=" * 60)

    while True:
        try:
            user_input = input("\n사용자: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n에이전트를 종료합니다. 감사합니다!")
            break

        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit", "종료", "끝"}:
            print("에이전트를 종료합니다. 감사합니다!")
            break

        messages.append({"role": "user", "content": user_input})

        while True:
            response = client.messages.create(
                model="claude-opus-4-7",
                max_tokens=8192,
                thinking={"type": "adaptive"},
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            )

            messages.append({"role": "assistant", "content": response.content})

            tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
            text_blocks = [b for b in response.content if b.type == "text"]

            for block in text_blocks:
                print(f"\n에이전트: {block.text}")

            if not tool_use_blocks:
                break

            tool_results = []
            for tool_use in tool_use_blocks:
                result_str = execute_tool(tool_use.name, tool_use.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": result_str,
                    }
                )

            messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    run_agent()
