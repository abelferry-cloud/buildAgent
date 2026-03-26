# s02: Tools - 实现效果

## 核心功能

### Tool 基类（agent/tools/base.py）

```python
class Tool(ABC):
    name: str
    description: str

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """执行工具逻辑"""
        pass

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "name": self.name,
            "description": self.description,
        }
```

### DispatchMap（agent/core/dispatch.py）

```python
class DispatchMap:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """注册工具"""
        self._tools[tool.name] = tool

    def dispatch(self, name: str, arguments: dict) -> ToolResult:
        """分发工具调用"""
        tool = self._tools.get(name)
        if not tool:
            return ToolResult(error=f"Tool '{name}' not found")
        return tool.execute(**arguments)
```

### 内置工具

| 工具 | 文件 | 功能 |
|------|------|------|
| `bash` | `builtin/bash.py` | 执行 Shell 命令 |
| `read` | `builtin/read.py` | 读取文件内容 |
| `write` | `builtin/write.py` | 写入文件 |
| `glob` | `builtin/glob.py` | 模式匹配文件 |

## Bug 修复记录

### 问题：write 工具未被成功执行

**现象**：Agent 能正确识别要使用 `write` 工具并生成正确的 JSON，但文件未被创建。

**根本原因**：`loop.py` 中的 `_parse_tool_calls()` 方法使用正则表达式 `\{(?:[^{}]|\{[^{}]*\})*\}` 只能处理一层嵌套花括号。当 LLM 返回的 JSON 内容包含 f-string（如 `f"Hello, {name}!"`）时，正则匹配失败。

**修复方案**：用**渐进式 JSON 解析**替代正则匹配：

```python
# 策略 2: 渐进式 JSON 提取
# 使用 json.loads 而不是脆弱的正则表达式
for start_idx in re.finditer(r'\{', response):
    start = start_idx.start()
    for end_offset in range(10, len(response) - start + 1):
        try:
            candidate = response[start:start + end_offset]
            data = json.loads(candidate)
            if "tool" in data and "args" in data:
                # 找到有效的工具调用
                ...
        except json.JSONDecodeError:
            continue
```

**验证**：测试 prompt `Create a file called greet.py with a greet(name) function` 成功创建文件。
