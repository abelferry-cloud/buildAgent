# s10: Team Protocols - 实现效果

## 核心功能

### ProtocolManager（agent/core/protocols.py）

```python
class ProtocolManager:
    """管理团队协议，协调 agent 之间的通信"""

    def __init__(self):
        self._teammate_manager = TeammateManager()
        self._request_protocol = RequestResponseProtocol(self._teammate_manager)
        self._notification_protocol = NotificationProtocol(self._teammate_manager)
        self._shutdown_requests: dict[str, ShutdownRequest] = {}
        self._plan_requests: dict[str, PlanApprovalRequest] = {}

    def create_shutdown_request(self, to: str, reason: str, from_: str = "") -> str:
        """创建 shutdown 请求"""

    def respond_shutdown(self, request_id: str, approve: bool, from_: str = "") -> None:
        """响应 shutdown 请求"""

    def create_plan_request(self, to: str, plan: str, from_: str = "") -> str:
        """创建计划审批请求"""

    def respond_plan(self, request_id: str, approve: bool, feedback: str = "", from_: str = "") -> None:
        """响应计划审批请求"""

    def send_notification(self, to: str, event: str, data: dict, from_: str = "") -> None:
        """发送通知"""
```

### 内置协议工具

| 工具 | 功能 |
|------|------|
| `protocol_shutdown_req` | 发送 shutdown 请求 |
| `protocol_shutdown_resp` | 响应 shutdown |
| `protocol_plan_req` | 发送计划审批请求 |
| `protocol_plan_resp` | 响应计划审批 |

## 集成

### main.py 初始化

```python
from agent.core.protocols import ProtocolManager

# Initialize ProtocolManager and wire it to protocol tools (s10: Team Protocols)
protocol_manager = ProtocolManager()
from agent.tools.builtin.protocol_shutdown_req import set_protocol_manager as set_shutdown_req
from agent.tools.builtin.protocol_shutdown_resp import set_protocol_manager as set_shutdown_resp
from agent.tools.builtin.protocol_plan_req import set_protocol_manager as set_plan_req
from agent.tools.builtin.protocol_plan_resp import set_protocol_manager as set_plan_resp

set_shutdown_req(protocol_manager)
set_shutdown_resp(protocol_manager)
set_plan_req(protocol_manager)
set_plan_resp(protocol_manager)
```

### dispatch.py 注册

```python
# Import and register protocol tools (s10: Team Protocols)
from agent.tools.builtin.protocol_shutdown_req import ProtocolShutdownReqTool
from agent.tools.builtin.protocol_shutdown_resp import ProtocolShutdownRespTool
from agent.tools.builtin.protocol_plan_req import ProtocolPlanReqTool
from agent.tools.builtin.protocol_plan_resp import ProtocolPlanRespTool

dispatch.register(ProtocolShutdownReqTool())
dispatch.register(ProtocolShutdownRespTool())
dispatch.register(ProtocolPlanReqTool())
dispatch.register(ProtocolPlanRespTool())
```

## 验证

```bash
python -c "from agent.core.protocols import ProtocolManager; pm = ProtocolManager(); print('OK')"
python -c "from agent.tools.builtin.protocol_shutdown_req import ProtocolShutdownReqTool; print('OK')"
```
