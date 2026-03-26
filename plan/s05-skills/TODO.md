# s05: Skills - TODO

## 官方定义

- **行数**: ~187 行
- **工具数**: 5 个
- **核心理念**: "Inject knowledge via tool_result when needed, not upfront in the system prompt"

## 待办事项

### ✅ 已完成
- [x] `SkillLoader` 骨架实现（`agent/core/skills.py`）
- [x] `LoadSkillTool` 工具 (`agent/tools/builtin/load_skill.py`)
- [x] **两层技能注入**:
  - [x] Layer 1: 系统提示只放技能名称和简短描述 (~100 tokens/skill)
  - [x] Layer 2: `load_skill` 工具按需加载完整内容 (~2000 tokens)
- [x] 技能目录结构: `skills/*/SKILL.md` + Python 包装器
- [x] 实际技能内容创建:
  - [x] `commit` - Git 提交规范
  - [x] `review-pr` - PR 代码审查
  - [x] `test` - 测试最佳实践
  - [x] `deploy` - 部署流程

### 验证方式
```bash
python main.py
```
试试这些 prompt (英文 prompt 对 LLM 效果更好, 也可以用中文):

What skills are available?
Load the agent-builder skill and follow its instructions
I need to do a code review -- load the relevant skill first
Build an MCP server using the mcp-builder skill
