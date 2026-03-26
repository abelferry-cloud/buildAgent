# s02: Tools - TODO

## 官方定义

- **行数**: ~120 行
- **工具数**: 4 个
- **核心理念**: "The loop stays the same; new tools register into the dispatch map"

## 待办事项

### ✅ 已完成
- [x] `Tool` 抽象基类（`agent/tools/base.py`）
- [x] `DispatchMap` 工具分发机制（`agent/core/dispatch.py`）
- [x] 内置工具注册：
  - [x] `bash` - Shell 命令执行
  - [x] `read` - 文件读取
  - [x] `write` - 文件写入
  - [x] `glob` - 文件模式匹配

### ✅ 已完成
- [x] Tool Schema OpenAI 格式兼容（`Tool.to_openai_function()`）
- [x] 工具描述规范化

### 验证方式
```bash
python main.py
```

试试这些 prompt (英文 prompt 对 LLM 效果更好, 也可以用中文):

- Read the file requirements.txt
- Create a file called greet.py with a greet(name) function
- Edit greet.py to add a docstring to the function
- Read greet.py to verify the edit worked
