# s11: Autonomous Agents - TODO

## 官方定义

- **行数**: ~499 行
- **工具数**: 14 个
- **核心理念**: "Teammates scan the board and claim tasks themselves"

## 待办事项

### ❌ 未完成
- [ ] `TaskBoard` 文件轮询（`agent/core/autonomous.py`）
- [ ] `AutonomousGovernor` 治理器

### 🔴 高优先级 - 需要加强
- [ ] **自动扫描 TaskBoard**: teammate 自动轮询可用任务
- [ ] **基于能力的任务认领**: 根据能力描述匹配任务
- [ ] **超时/重试/升级逻辑完善**
- [ ] `self_correct()` 实际逻辑实现
- [ ] 错误分类和自动恢复策略

### 验证方式
```bash
python -c "from agent.core.autonomous import TaskBoard, AutonomousGovernor; print('OK')"
```
