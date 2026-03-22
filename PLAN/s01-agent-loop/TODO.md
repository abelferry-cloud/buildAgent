# s01: Agent Loop - TODO

## 官方定义

- **行数**: ~84 行
- **工具数**: 1 个
- **核心理念**: "The minimal agent kernel is a while loop + one tool"

## 待办事项

### ✅ 已完成
- [x] `Agent` 类实现 while 循环
- [x] 单工具执行机制
- [x] `Message` 和 `AgentResponse` 数据类
- [x] 基础的 step() 方法
- [x] LLM 客户端集成（DeepSeek）
- [x] 多步迭代执行（直到 done=True）
- [x] 工具输出显示在响应中

### 验证方式
```bash
python main.py
```


试试这些 prompt (英文 prompt 对 LLM 效果更好, 也可以用中文):

- Create a file called hello.py that prints "Hello, World!"
- List all Python files in this directory
- What is the current git branch?
- Create a directory called test_output and write 3 files in it
