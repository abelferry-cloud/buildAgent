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
python main.py
```
试试这些 prompt (英文 prompt 对 LLM 效果更好, 也可以用中文):

Run "sleep 5 && echo done" in the background, then create a file while it runs
Start 3 background tasks: "sleep 2", "sleep 4", "sleep 6". Check their status.
Run pytest in the background and keep working on other things
