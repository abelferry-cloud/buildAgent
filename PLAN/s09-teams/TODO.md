# s09: Agent Teams - TODO

## 官方定义

- **行数**: ~348 行
- **工具数**: 10 个
- **核心理念**: "When one agent can't finish, delegate to persistent teammates via async mailboxes"

## 待办事项

### ✅ 已完成
- [x] `TeammateManager` 团队管理器（`agent/core/teams.py`）
- [x] 文件-based 邮箱系统（`agent/state/mailbox.py`）
- [x] 异步消息传递
- [x] 内置工具:
  - [x] `team_send` - 发送消息
  - [x] `team_broadcast` - 广播消息
  - [x] `team_list` - 列出团队成员
  - [x] `team_status` - 查看状态
- [x] TeammateManager 在 `main.py` 中初始化并连接到 team tools
- [x] Team tools 在 `agent/core/dispatch.py` 中注册

### 🔴 高优先级
- [ ] 团队成员健康检查
- [ ] 消息重试机制

### 验证方式
```bash
python -c "from agent.core.teams import TeammateManager; print('OK')"
```
