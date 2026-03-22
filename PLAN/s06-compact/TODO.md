# s06: Compact - TODO

## 官方定义

- **行数**: ~205 行
- **工具数**: 5 个
- **核心理念**: "Context will fill up; three-layer compression strategy enables infinite sessions"

## 待办事项

### ❌ 未完成
- [ ] 三层压缩策略（`agent/core/compact.py`）
- [ ] Micro-compact: 空格移除
- [ ] Auto-compact: 消息摘要
- [ ] Archive: 旧消息归档到文件

### 验证方式
```bash
python -c "from agent.core.compact import Compact; print('OK')"
```
