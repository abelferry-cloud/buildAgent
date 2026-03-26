# s10: Team Protocols - TODO

## 官方定义

- **行数**: ~419 行
- **工具数**: 12 个
- **核心理念**: "One request-response pattern drives all team negotiation"

## 待办事项

### ✅ 已完成
- [x] `ProtocolManager` 协议管理器（`agent/core/protocols.py`）
- [x] Shutdown Protocol 实现:
  - [x] `shutdown_request` → `shutdown_response` (approve/reject)
  - [x] `shutdown_requests` 追踪器
- [x] Plan Approval Protocol 实现:
  - [x] `plan_req` → `plan_resp` (approve/reject)
  - [x] `plan_requests` 追踪器
- [x] 内置工具:
  - [x] `protocol_shutdown_req` - 发送 shutdown 请求
  - [x] `protocol_shutdown_resp` - 响应 shutdown
  - [x] `protocol_plan_req` - 发送计划审批请求
  - [x] `protocol_plan_resp` - 响应计划审批
- [x] ProtocolManager 在 `main.py` 中初始化并连接到 protocol tools
- [x] Protocol tools 在 `agent/core/dispatch.py` 中注册

### 验证方式
```bash
python main.py
```

试试这些 prompt (英文 prompt 对 LLM 效果更好, 也可以用中文):

Spawn alice as a coder. Then request her shutdown.
List teammates to see alice's status after shutdown approval
Spawn bob with a risky refactoring task. Review and reject his plan.
Spawn charlie, have him submit a plan, then approve it.
输入 /team 监控状态
