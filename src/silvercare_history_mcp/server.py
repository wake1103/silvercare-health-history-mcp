from datetime import datetime, timezone
from typing import Annotated, Literal

from mcp.server import MCPServer
from pydantic import Field

mcp = MCPServer("SilverCare-Health-History")

MetricType = Literal["heart_rate", "blood_pressure", "temperature", "spo2"]

# 模拟历史健康记录（开发阶段，data_source = simulated）
MOCK_HISTORY = {
    "user_001": {
        "heart_rate": [
            {
                "record_id": "hr_000",
                "timestamp": "2026-10-25T08:00:00Z",
                "value": 75,
                "unit": "bpm",
                "source": "simulated_device",
            },
            {
                "record_id": "hr_001",
                "timestamp": "2026-10-30T08:00:00Z",
                "value": 78,
                "unit": "bpm",
                "source": "simulated_device",
            },
            {
                "record_id": "hr_002",
                "timestamp": "2026-10-31T08:00:00Z",
                "value": 81,
                "unit": "bpm",
                "source": "simulated_device",
            },
            {
                "record_id": "hr_003",
                "timestamp": "2026-11-01T08:00:00Z",
                "value": 83,
                "unit": "bpm",
                "source": "simulated_device",
            },
        ],
        "blood_pressure": [
            {
                "record_id": "bp_001",
                "timestamp": "2026-10-30T09:00:00Z",
                "value": {"systolic": 120, "diastolic": 78},
                "unit": "mmHg",
                "source": "simulated_device",
            }
        ],
        "temperature": [
            {
                "record_id": "temp_001",
                "timestamp": "2026-10-30T10:00:00Z",
                "value": 36.6,
                "unit": "°C",
                "source": "simulated_device",
            }
        ],
        "spo2": [
            {
                "record_id": "spo2_001",
                "timestamp": "2026-10-30T11:00:00Z",
                "value": 97,
                "unit": "%",
                "source": "simulated_device",
            }
        ],
    }
}


def _parse_time(value: str, field_name: str) -> datetime:
    """解析带时区的 ISO 8601 时间，并统一转换为 UTC。"""
    normalized = value[:-1] + "+00:00" if value.endswith(("Z", "z")) else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid ISO 8601 datetime") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field_name} must include a timezone, for example Z or +08:00")
    return parsed.astimezone(timezone.utc)


def _error_response(
    user_id: str, metric_type: str, code: str, message: str
) -> dict:
    return {
        "success": False,
        "user_id": user_id,
        "metric_type": metric_type,
        "data_source": "simulated",
        "records": [],
        "total": 0,
        "error": {"code": code, "message": message},
    }


@mcp.tool()
async def get_health_history(
    user_id: Annotated[str, Field(description="用户唯一标识")],
    metric_type: Annotated[MetricType, Field(description="要查询的健康指标类型")],
    start_time: Annotated[str, Field(description="查询开始时间，ISO 8601格式")],
    end_time: Annotated[str, Field(description="查询结束时间，ISO 8601格式")],
    limit: Annotated[
        int, Field(ge=1, le=100, description="最多返回的记录数量")
    ] = 20,
) -> dict:
    """按用户ID、指标类型和时间范围查询历史健康记录。只返回数据，不进行诊断。"""
    try:
        start = _parse_time(start_time, "start_time")
        end = _parse_time(end_time, "end_time")
    except ValueError as exc:
        return _error_response(
            user_id, metric_type, "INVALID_TIME_FORMAT", str(exc)
        )

    if start > end:
        return _error_response(
            user_id,
            metric_type,
            "INVALID_TIME_RANGE",
            "start_time must be earlier than or equal to end_time",
        )

    user_history = MOCK_HISTORY.get(user_id)
    if user_history is None:
        return _error_response(
            user_id, metric_type, "USER_NOT_FOUND", "No history found for this user"
        )

    records = [
        record
        for record in user_history[metric_type]
        if start <= _parse_time(record["timestamp"], "timestamp") <= end
    ]
    records.sort(key=lambda record: _parse_time(record["timestamp"], "timestamp"))

    # limit 超过匹配数量时返回全部；否则保留最新 N 条，并按时间升序返回。
    records = records[-limit:]

    return {
        "success": True,
        "user_id": user_id,
        "metric_type": metric_type,
        "data_source": "simulated",
        "records": records,
        "total": len(records),
        "error": None,
    }
