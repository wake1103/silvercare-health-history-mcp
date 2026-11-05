# SilverCare Health History MCP

SilverCare 历史健康记录查询 MCP 服务。当前使用模拟数据，只返回符合条件的记录，不计算健康结论，不执行诊断或风险判断。

## 工具：`get_health_history`

按用户 ID、指标类型和闭区间时间范围查询历史记录。

### 输入参数

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `user_id` | string | 是 | 用户唯一标识；模拟用户为 `user_001` |
| `metric_type` | string | 是 | `heart_rate`、`blood_pressure`、`temperature`、`spo2` |
| `start_time` | string | 是 | ISO 8601 开始时间，必须带时区，如 `2026-10-26T00:00:00Z` |
| `end_time` | string | 是 | ISO 8601 结束时间，必须带时区 |
| `limit` | integer | 否 | 1～100，默认 20；超过匹配数量时返回全部，否则保留最新 N 条 |

返回记录按时间升序排列。`total` 是本次实际返回的记录数，每条记录包含 `record_id`、`timestamp`、`value`、`unit` 和 `source`。

### 查询示例

```json
{
  "user_id": "user_001",
  "metric_type": "heart_rate",
  "start_time": "2026-10-26T00:00:00Z",
  "end_time": "2026-11-02T23:59:59Z",
  "limit": 20
}
```

成功时返回：

```json
{
  "success": true,
  "user_id": "user_001",
  "metric_type": "heart_rate",
  "data_source": "simulated",
  "records": [
    {
      "record_id": "hr_001",
      "timestamp": "2026-10-30T08:00:00Z",
      "value": 78,
      "unit": "bpm",
      "source": "simulated_device"
    },
    {
      "record_id": "hr_002",
      "timestamp": "2026-10-31T08:00:00Z",
      "value": 81,
      "unit": "bpm",
      "source": "simulated_device"
    },
    {
      "record_id": "hr_003",
      "timestamp": "2026-11-01T08:00:00Z",
      "value": 83,
      "unit": "bpm",
      "source": "simulated_device"
    }
  ],
  "total": 3,
  "error": null
}
```

没有匹配记录时仍返回 `success=true`、`records=[]` 和 `total=0`。参数或用户错误包括 `INVALID_TIME_FORMAT`、`INVALID_TIME_RANGE`、`USER_NOT_FOUND`；指标枚举和 `limit` 范围由 MCP Schema 校验。

## 本地运行

要求 Python 3.10 或更高版本。

```bash
pip install -e .
python -m silvercare_history_mcp
```

默认使用 stdio。启动 Streamable HTTP：

```bash
MCP_TRANSPORT=streamable-http python -m silvercare_history_mcp
```

HTTP 默认监听 `0.0.0.0:8000`，路径为 `/mcp`，使用无状态模式。可通过 `MCP_HOST`、`MCP_PORT` 修改监听地址。

## 运行测试

```bash
python -m unittest discover -s tests -v
```

## UVX

从 PyPI 运行：

```bash
uvx --from silvercare-health-history-mcp==0.1.0 silvercare-history-mcp
```

从 GitHub 运行：

```bash
uvx --from git+https://github.com/wake1103/silvercare-health-history-mcp.git silvercare-history-mcp
```

## AgentArts 接入

AgentArts 是公有云服务，无法访问本地或内网。UVX 由平台托管运行；HTTP 方式必须部署到公网可访问地址。

### UVX（推荐）

选择 **UVX**，使用 JSON 编辑：

```json
{
  "mcpServers": {
    "silvercare-health-history": {
      "command": "uvx",
      "args": [
        "--from",
        "silvercare-health-history-mcp==0.1.0",
        "silvercare-history-mcp"
      ]
    }
  }
}
```

### Streamable HTTP（备选）

将服务部署到公网后，选择 **Streamable HTTP**，Endpoint 填：

```text
https://<YOUR_PUBLIC_DOMAIN>/mcp
```

```json
{
  "mcpServers": {
    "silvercare-health-history": {
      "url": "https://<YOUR_PUBLIC_DOMAIN>/mcp"
    }
  }
}
```
