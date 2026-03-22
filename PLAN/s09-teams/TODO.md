# s09: Agent Teams - TODO

## 官方定义

- **行数**: ~348 行
- **工具数**: 10 个
- **核心理念**: "When one agent can't finish, delegate to persistent teammates via async mailboxes"

## 待办事项

### ❌ 未完成
- [ ] `TeammateManager` 团队管理器（`agent/core/teams.py`）
- [ ] 文件-based 邮箱系统（`agent/state/mailbox.py`）
- [ ] 异步消息传递
- [ ] 内置工具:
  - [ ] `team_send` - 发送消息
  - [ ] `team_broadcast` - 广播消息
  - [ ] `team_list` - 列出团队成员
  - [ ] `team_status` - 查看状态

### 🔴 高优先级
- [ ] 团队成员健康检查
- [ ] 消息重试机制

### 验证方式
```bash
python -c "from agent.core.teams import TeammateManager; print('OK')"
```
