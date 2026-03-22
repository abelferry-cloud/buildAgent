# s10: Team Protocols - TODO

## 官方定义

- **行数**: ~419 行
- **工具数**: 12 个
- **核心理念**: "One request-response pattern drives all team negotiation"

## 待办事项

### ❌ 未完成
- [ ] `request_id` 生成器和关联机制
- [ ] **Shutdown Protocol**:
  - [ ] `shutdown_request` → `shutdown_response` (approve/reject)
  - [ ] FSM 状态机: `pending → approved | rejected`
  - [ ] `shutdown_requests` 追踪器
- [ ] **Plan Approval Protocol**:
  - [ ] `plan_req` → `plan_resp` (approve/reject)
  - [ ] `plan_requests` 追踪器
- [ ] 协议超时处理
- [ ] 协议重试机制

### 验证方式
```bash
python -c "from agent.core.protocols import ProtocolManager; print('OK')"
```
