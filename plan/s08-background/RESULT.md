# s08: Background Tasks - 实现效果

## 核心功能

### BackgroundManager（agent/core/background.py）

后台任务管理器，支持异步后台执行和线程池执行。

```python
class JobStatus(Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class BackgroundJob:
    id: str
    name: str
    status: JobStatus
    result: Any | None = None
    error: str | None = None
    created_at: float = field(default_factory=time.time)
    completed_at: float | None = None

class BackgroundManager:
    def __init__(self, notification_queue: NotificationQueue | None = None):
        self._jobs: dict[str, BackgroundJob] = {}
        self._futures: dict[str, Future] = {}
        self._executor = threading.Thread(target=self._run_loop, daemon=True)
        self._executor.start()

    def run_in_background(self, name: str, coro_ref: str) -> str:
        """启动后台任务（存储协程引用）"""

    def run_in_background_sync(self, name: str, coro: Callable) -> str:
        """启动同步函数到后台线程执行"""

    def get_status(self, job_id: str) -> BackgroundJob:
        """获取任务状态"""

    def wait(self, job_id: str, timeout: Optional[float] = None) -> Any:
        """等待任务完成"""

    def cancel(self, job_id: str) -> bool:
        """取消任务"""

    def list_jobs(self) -> list[BackgroundJob]:
        """列出所有任务"""
```

### 内置后台工具

| 工具 | 功能 |
|------|------|
| `background_run` | 启动后台任务 |
| `background_wait` | 等待任务完成 |
| `background_cancel` | 取消任务 |

## 集成

### main.py 初始化

```python
from agent.core.background import BackgroundManager

# Initialize BackgroundManager and wire it to background tools (s08: Background Tasks)
background_manager = BackgroundManager()
from agent.tools.builtin.background_run import set_background_manager as set_bg_run
from agent.tools.builtin.background_wait import set_background_manager as set_bg_wait
from agent.tools.builtin.background_cancel import set_background_manager as set_bg_cancel

set_bg_run(background_manager)
set_bg_wait(background_manager)
set_bg_cancel(background_manager)
```

### dispatch.py 注册

```python
# Import and register background tools (s08: Background Tasks)
from agent.tools.builtin.background_run import BackgroundRunTool
from agent.tools.builtin.background_wait import BackgroundWaitTool
from agent.tools.builtin.background_cancel import BackgroundCancelTool

dispatch.register(BackgroundRunTool())
dispatch.register(BackgroundWaitTool())
dispatch.register(BackgroundCancelTool())
```

## 优势

- Agent 可以在等待慢操作时继续思考
- 支持超时控制和任务取消
- 任务结果存储供后续使用
- 线程池执行避免阻塞主线程
- 通知队列集成

## 验证

```bash
python -c "from agent.core.background import BackgroundManager; bm = BackgroundManager(); print('OK')"
python -c "from agent.tools.builtin.background_run import BackgroundRunTool; print('OK')"
```
