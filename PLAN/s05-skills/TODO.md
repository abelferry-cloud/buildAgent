# s05: Skills - TODO

## 官方定义

- **行数**: ~187 行
- **工具数**: 5 个
- **核心理念**: "Inject knowledge via tool_result when needed, not upfront in the system prompt"

## 待办事项

### ❌ 未完成
- [ ] `SkillLoader` 骨架实现（`agent/skills/loader.py`）

### 🔴 高优先级
- [ ] **两层技能注入**:
  - [ ] Layer 1: 系统提示只放技能名称和简短描述 (~100 tokens/skill)
  - [ ] Layer 2: `load_skill` 工具按需加载完整内容 (~2000 tokens)
- [ ] 技能目录结构: `skills/*/SKILL.md` + YAML frontmatter
- [ ] 实际技能内容创建:
  - [ ] `commit` - Git 提交规范
  - [ ] `review-pr` - PR 代码审查
  - [ ] `test` - 测试最佳实践
  - [ ] `deploy` - 部署流程

### 验证方式
```bash
python -c "from agent.skills.loader import SkillLoader; print('OK')"
```
