# S10: Team Protocols - 总结

## 核心理念

> Two-way request/response and fire-and-forget notification protocols

## 核心原理

S10 实现了两种协议机制，用于代理之间的结构化通信：

1. **Request-Response Protocol** - 双向请求/响应，带 request_id 关联
2. **Notification Protocol** - 火灾即忘的通知，支持订阅/退订

### Request-Response 协议

- **唯一请求 ID** - 每个请求有唯一标识
- **Future 模式** - 使用 `RequestFuture` 追踪pending请求
- **超时控制** - 支持请求超时设置
- **取消机制** - 可中止pending的请求

### Notification 协议

- **发布/订阅** - 订阅者注册处理器
- **广播通知** - 向所有订阅者发送通知
- **解耦通信** - 发布者不需要知道订阅者

## 关键类/组件

| 名称 | 文件 | 职责 |
|------|------|------|
| `RequestFuture` | `agent/core/protocols.py` | pending请求的Future封装 |
| `RequestResponseProtocol` | `agent/core/protocols.py` | 请求/响应协议实现 |
| `NotificationProtocol` | `agent/core/protocols.py` | 通知协议实现 |
| `ProtocolManager` | `agent/core/protocols.py` | 统一协议接口 |

## 涉及的文件

### 核心文件
- `agent/core/protocols.py` - 协议管理器
- `agent/protocols/base.py` - 协议基类和消息类型

### 工具文件
- `agent/tools/builtin/protocol_shutdown_req.py` - ProtocolShutdownReqTool
- `agent/tools/builtin/protocol_shutdown_resp.py` - ProtocolShutdownRespTool
- `agent/tools/builtin/protocol_plan_req.py` - ProtocolPlanReqTool
- `agent/tools/builtin/protocol_plan_resp.py` - ProtocolPlanRespTool

## 与 main.py 的集成

```python
from agent.core.protocols import ProtocolManager

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

## 工具列表

| 工具名 | 类 | 功能 |
|--------|-----|------|
| `protocol_shutdown_req` | ProtocolShutdownReqTool | 请求队友关闭 |
| `protocol_shutdown_resp` | ProtocolShutdownRespTool | 同意/拒绝关闭请求 |
| `protocol_plan_req` | ProtocolPlanReqTool | 请求队友审批计划 |
| `protocol_plan_resp` | ProtocolPlanRespTool | 同意/拒绝计划（可带反馈） |

## 架构图

```
┌─────────────────────────────────────────┐
│         ProtocolManager                  │
│  ┌───────────────────────────────────┐  │
│  │ _request_protocol: RequestResponse│  │
│  │ _notification_protocol: Notification│  │
│  └───────────────────────────────────┘  │
│  create_shutdown_request() │ respond_shutdown()
│  create_plan_request() │ respond_plan()
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────┐  ┌─────────────────────┐
│RequestResponseProtocol│  │NotificationProtocol │
│  ┌───────────────┐  │  │  ┌───────────────┐  │
│  │_futures: dict │  │  │  │_handlers: list│  │
│  │ (request_id)  │  │  │  │ (订阅者)      │  │
│  └───────────────┘  │  │  └───────────────┘  │
│  send_request()     │  │  send_notification()│
│  handle_response()  │  │  subscribe()        │
└─────────────────────┘  └─────────────────────┘

Request-Response 流程:
  A ── request_id=xxx ──► B
  A ◄──── response ────── B
       (通过 future 获取)

Notification 流程:
  发布者 ─── broadcast ──► 订阅者1
                       └──► 订阅者2
```

## 特殊请求类型

| 类型 | 数据结构 | 说明 |
|------|----------|------|
| `ShutdownRequest` | `{reason, requester}` | 关闭请求 |
| `PlanApprovalRequest` | `{plan, requester, feedback}` | 计划审批请求 |
