# s11: Autonomous Agents - TODO

## 官方定义

- **行数**: ~499 行
- **工具数**: 14 个
- **核心理念**: "Teammates scan the board and claim tasks themselves"

## 待办事项

### ✅ 已完成
- [x] `TaskBoard` 文件轮询（`agent/core/autonomous.py`）
- [x] `AutonomousGovernor` 治理器
- [x] 内置工具:
  - [x] `board_post` - 发布任务到任务板
  - [x] `board_poll` - 轮询可用任务
  - [x] `board_claim` - 认领特定任务
  - [x] `board_complete` - 完成任务
- [x] TaskBoard 在 `main.py` 中初始化并连接到 board tools
- [x] Board tools 在 `agent/core/dispatch.py` 中注册

### 验证方式
```bash
python -c "from agent.core.autonomous import TaskBoard, AutonomousGovernor; print('OK')"
```
