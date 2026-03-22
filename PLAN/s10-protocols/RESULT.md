# s10: Team Protocols - 待实现

## 目标功能

### 协议架构

```
Request → FSM (pending) → Response (approved/rejected)
```

### Shutdown Protocol

```python
@dataclass
class ShutdownRequest:
    request_id: str
    from_agent: str
    to_agent: str
    reason: str
    timestamp: float

class ShutdownProtocol:
    def __init__(self):
        self._pending: dict[str, ShutdownRequest] = {}
        self._responses: dict[str, bool] = {}  # request_id -> approved?

    def request_shutdown(self, to: str, reason: str) -> str:
        """发送 shutdown 请求"""
        request_id = generate_uuid()
        self._pending[request_id] = ShutdownRequest(...)
        return request_id

    def respond_shutdown(self, request_id: str, approve: bool) -> None:
        """响应 shutdown 请求"""
        self._responses[request_id] = approve
        self._pending.pop(request_id)

    def get_status(self, request_id: str) -> str:
        """获取请求状态"""
        if request_id in self._pending:
            return "pending"
        if request_id in self._responses:
            return "approved" if self._responses[request_id] else "rejected"
        return "unknown"
```

### Plan Approval Protocol

```python
@dataclass
class PlanApprovalRequest:
    request_id: str
    from_agent: str
    plan: str
    timestamp: float

class PlanApprovalProtocol:
    """计划审批协议"""
    pass
```

### 协议工具

| 工具 | 功能 |
|------|------|
| `protocol_shutdown_req` | 发送 shutdown 请求 |
| `protocol_shutdown_resp` | 响应 shutdown |
| `protocol_plan_req` | 发送计划审批请求 |
| `protocol_plan_resp` | 响应计划审批 |
