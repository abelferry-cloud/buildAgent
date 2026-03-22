# s04: Subagents - TODO

## 官方定义

- **行数**: ~151 行
- **工具数**: 5 个
- **核心理念**: "Subagents use independent messages[], keeping the main conversation clean"

## 待办事项

### ✅ 已完成
- [x] `SubagentManager` 子代理管理器 (`agent/core/subagent.py`)
- [x] `spawn` 工具 - 派生子代理 (`agent/tools/builtin/spawn.py`)
- [x] 独立消息空间 (每个 Subagent 有自己的 messages[])
- [x] 主对话清洁（隔离）- send/receive 机制

### 验证方式
```bash
python -c "from agent.core.subagent import SubagentManager; print('OK')"
```
