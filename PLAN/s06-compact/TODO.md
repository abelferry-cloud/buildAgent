# s06: Compact - TODO

## 官方定义

- **行数**: ~205 行
- **工具数**: 5 个
- **核心理念**: "Context will fill up; three-layer compression strategy enables infinite sessions"

## 待办事项

### ✅ 已完成
- [x] 三层压缩策略（`agent/core/compact.py` + `agent/utils/compression.py`）
- [x] Micro-compact: 空格移除
- [x] Auto-compact: 消息摘要
- [x] Archive: 旧消息归档到文件
- [x] `CompressionManager` 集成到 `Agent` (`agent/core/loop.py`)
- [x] `CompressionManager` 在 `main.py` 中初始化

### 验证方式
```bash
python -c "from agent.core.compact import CompressionManager, CompressionConfig; print('OK')"
```
