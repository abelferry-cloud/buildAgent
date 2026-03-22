# S06: Compact (Message Compression) - 总结

## 核心理念

> Three-layer compression: micro → auto → archive

## 核心原理

S06 实现了三层消息压缩系统，用于管理不断增长的对话历史。

### 三层压缩机制

1. **Micro-compact（微观压缩）**
   - 单条消息级别
   - 移除空白字符
   - 工具名缩写（如 `bash` → `bsh`）
   - 仅对超过阈值长度的消息应用

2. **Auto-compact（自动压缩）**
   - 消息集级别
   - 当消息数达到阈值时调用
   - 保留最近一半消息
   - 对旧消息生成摘要

3. **Archive（归档）**
   - 文件级别
   - 超过消息数阈值时触发
   - 将旧消息移动到 `.agent_archive/` 目录
   - 需要时可恢复

## 关键类/组件

| 名称 | 文件 | 职责 |
|------|------|------|
| `CompressionConfig` | `agent/core/compact.py` | 压缩配置参数 |
| `CompressionManager` | `agent/core/compact.py` | 三层压缩协调器 |
| `MicroCompressor` | `agent/utils/compression.py` | 微观压缩实现 |
| `AutoCompressor` | `agent/utils/compression.py` | 自动压缩实现 |
| `ArchivalCompressor` | `agent/utils/compression.py` | 归档压缩实现 |

## 涉及的文件

### 核心文件
- `agent/core/compact.py` - CompressionManager
- `agent/utils/compression.py` - 三种压缩器实现

### 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `micro_compact_threshold` | 100 | 微观压缩字符阈值 |
| `auto_compact_interval` | 50 | 自动压缩消息间隔 |
| `archive_after_messages` | 100 | 归档消息数阈值 |

## 与 main.py 的集成

```python
from agent.core.compact import CompressionManager, CompressionConfig

config = CompressionConfig(
    micro_compact_threshold=100,
    auto_compact_interval=50,
    archive_after_messages=100,
)

compression_manager = CompressionManager(agent=agent, config=config)
agent._compression_manager = compression_manager
```

## 架构图

```
┌─────────────────────────────────────────┐
│       CompressionManager                │
│  ┌───────────────────────────────────┐  │
│  │ _agent: Agent                    │  │
│  │ _config: CompressionConfig       │  │
│  │ _archive_dir: ".agent_archive"    │  │
│  └───────────────────────────────────┘  │
│  compress_if_needed()                  │
│       │                                 │
│       ├──► micro_compact()   (单消息)   │
│       ├──► auto_compact()    (消息集)  │
│       └──► archive()         (文件)    │
└─────────────────────────────────────────┘

触发顺序:
micro_compact: 消息长度 > 100 字符
auto_compact: 消息数达到 50
archive: 消息数达到 100
```

## 压缩效果示例

**Micro-compact 前:**
```
"bash" → "Execute a shell command"
```

**Auto-compact 前 (50条消息):**
```
[30条旧消息] → 被摘要 → "Summary: 30 messages, used tools: bash, read, write"
[20条新消息保持原样]
```
