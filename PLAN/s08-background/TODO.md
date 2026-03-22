# s08: Background Tasks - TODO

## 官方定义

- **行数**: ~198 行
- **工具数**: 6 个
- **核心理念**: "Run slow operations in the background; the agent keeps thinking ahead"

## 待办事项

### ✅ 已完成
- [x] `BackgroundManager` 后台任务运行器（`agent/core/background.py`）
- [x] 异步后台执行
- [x] 内置工具:
  - [x] `background_run` - 后台执行任务
  - [x] `background_wait` - 等待任务完成
  - [x] `background_cancel` - 取消任务
- [x] BackgroundManager 在 `main.py` 中初始化并连接到 background tools
- [x] Background tools 在 `agent/core/dispatch.py` 中注册

### 验证方式
```bash
python -c "from agent.core.background import BackgroundManager; bm = BackgroundManager(); print('OK')"
python -c "from agent.tools.builtin.background_run import BackgroundRunTool; print('OK')"
```
