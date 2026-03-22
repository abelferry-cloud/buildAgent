# s08: Background Tasks - 实现效果

## 核心功能

### BackgroundRunner（agent/core/background.py）

```python
class BackgroundRunner:
    """后台任务运行器，支持异步执行"""

    def __init__(self):
        self._tasks: dict[str, asyncio.Task] = {}
        self._results: dict[str, Any] = {}

    async def run(self, name: str, coro: coroutine) -> str:
        """后台运行协程"""
        task = asyncio.create_task(coro)
        self._tasks[name] = task
        return f"Started background task: {name}"

    async def wait(self, name: str, timeout: float = None) -> Any:
        """等待任务完成"""
        if name not in self._tasks:
            return None
        try:
            return await asyncio.wait_for(self._tasks[name], timeout)
        except asyncio.TimeoutError:
            return None

    def cancel(self, name: str) -> bool:
        """取消任务"""
        if name in self._tasks:
            self._tasks[name].cancel()
            return True
        return False
```

### 内置后台工具

| 工具 | 功能 |
|------|------|
| `background_run` | 后台执行任务 |
| `background_wait` | 等待任务完成 |
| `background_cancel` | 取消任务 |

## 优势

- Agent 可以在等待慢操作时继续思考
- 支持超时控制和任务取消
- 任务结果存储供后续使用
