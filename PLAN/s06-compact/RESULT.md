# s06: Compact - 实现效果

## 三层压缩策略

### Layer 1: Micro-compact
去除每条消息的无关空格

```python
def micro_compact(self, text: str) -> str:
    """移除空格、换行"""
    return re.sub(r'\s+', ' ', text).strip()
```

### Layer 2: Auto-compact
当消息数超过阈值时，摘要旧消息

```python
def auto_compact(self, messages: list[Message], threshold: int = 20) -> list[Message]:
    """摘要旧消息"""
    if len(messages) <= threshold:
        return messages

    summary = self.summarize(messages[:-threshold])
    return [Message(role="system", content=f"Summary: {summary}")] + messages[-threshold:]
```

### Layer 3: Archive
将旧消息归档到文件存储

```python
def archive(self, messages: list[Message]) -> list[Message]:
    """归档旧消息到文件"""
    archived = messages[:-10]  # 保留最近 10 条
    self._store.archive(archived)
    return messages[-10:]
```

## 效果

支持无限长度的会话，通过压缩保持上下文在合理大小。
