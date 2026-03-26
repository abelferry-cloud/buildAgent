# s06: Compact - 实现效果

## 三层压缩策略

### Layer 1: Micro-compact
去除每条消息的无关空格，缩短工具名称

```python
class MicroCompressor:
    def __init__(self, threshold: int = 100):
        self.threshold = threshold

    def compact(self, message: Message) -> Message:
        # 移除空格、缩短工具名称
        content = re.sub(r"\s+", " ", content)
        # 工具名缩写: bash->bsh, read->rd, write->wr...
```

### Layer 2: Auto-compact
当消息数超过阈值时，摘要旧消息

```python
class AutoCompressor:
    def __init__(self, interval: int = 50):
        self.interval = interval

    def compact(self, messages: list[Message]) -> list[Message]:
        # 保留最近 interval//2 条，摘要其余消息
        summary = self._summarize_messages(older)
        return [Message(role="system", content=f"[Previous {len(older)} messages summarized]: {summary}")] + recent
```

### Layer 3: Archive
将旧消息归档到文件存储

```python
class ArchivalCompressor:
    def __init__(self, archive_dir: str = ".agent_archive", after_messages: int = 100):
        self.archive_dir = archive_dir

    def archive(self, messages: list[Message], archive_id: str) -> ArchivedMessages:
        # 保留最近 after_messages 条，其余写入 .agent_archive/{archive_id}.json
```

## 集成

### CompressionManager (`agent/core/compact.py`)

```python
@dataclass
class CompressionConfig:
    micro_compact_threshold: int = 100
    auto_compact_interval: int = 50
    archive_after_messages: int = 100

class CompressionManager:
    def __init__(self, agent: Agent, config: CompressionConfig | None = None):
        self._micro = MicroCompressor(threshold=config.micro_compact_threshold)
        self._auto = AutoCompressor(interval=config.auto_compact_interval)
        self._archive = ArchivalCompressor(after_messages=config.archive_after_messages)

    def compress_if_needed(self, messages: list[Message]) -> list[Message]:
        # Layer 3: Archive check (largest threshold)
        # Layer 2: Auto-compact check
        # Layer 1: Micro-compact per message
```

### Agent 集成 (`agent/core/loop.py`)

```python
def __init__(self, ..., compression_manager: Optional[Any] = None):
    self._compression_manager = compression_manager

# 在 _llm_step 中，工具执行后调用:
if self._compression_manager:
    self.messages = self._compression_manager.compress_if_needed(self.messages)
```

### main.py 初始化

```python
from agent.core.compact import CompressionManager, CompressionConfig

config = CompressionConfig(
    micro_compact_threshold=100,
    auto_compact_interval=50,
    archive_after_messages=100,
)

agent = Agent(...)
compression_manager = CompressionManager(agent=agent, config=config)
agent._compression_manager = compression_manager
```

## 效果

支持无限长度的会话，通过压缩保持上下文在合理大小。

## 验证

```bash
python -c "from agent.core.compact import CompressionManager, CompressionConfig; print('OK')"
```
