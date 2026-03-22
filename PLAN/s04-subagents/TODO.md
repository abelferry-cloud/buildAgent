# s04: Subagents - TODO

## 官方定义

- **行数**: ~151 行
- **工具数**: 5 个
- **核心理念**: "Subagents use independent messages[], keeping the main conversation clean"

## 待办事项

### ❌ 未完成
- [ ] `SubagentManager` 子代理管理器
- [ ] `spawn` 工具 - 派生子代理
- [ ] 独立消息空间
- [ ] 主对话清洁（隔离）

### 验证方式
```bash
python -c "from agent.core.subagent import SubagentManager; print('OK')"
```
