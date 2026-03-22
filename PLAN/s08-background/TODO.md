# s08: Background Tasks - TODO

## 官方定义

- **行数**: ~198 行
- **工具数**: 6 个
- **核心理念**: "Run slow operations in the background; the agent keeps thinking ahead"

## 待办事项

### ❌ 未完成
- [ ] `BackgroundRunner` 后台任务运行器（`agent/core/background.py`）
- [ ] 异步后台执行
- [ ] 内置工具:
  - [ ] `background_run` - 后台执行任务
  - [ ] `background_wait` - 等待任务完成
  - [ ] `background_cancel` - 取消任务

### 验证方式
```bash
python -c "from agent.core.background import BackgroundRunner; print('OK')"
```
