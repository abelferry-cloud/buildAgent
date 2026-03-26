# s05: Skills - 实现效果

## 核心功能

### 两层技能注入架构

| Layer | 时机 | 内容 | Token Budget |
|------|------|------|--------------|
| Layer 1 | 系统提示 | 技能名称 + 简短描述 | ~100 tokens/skill |
| Layer 2 | `load_skill` tool | 按需加载完整内容 | ~2000 tokens |

### SkillLoader（agent/core/skills.py）

```python
class SkillLoader:
    def __init__(self, skills_dir: str):
        self.skills_dir = skills_dir
        self._skills: dict[str, Skill] = {}
        self._load_all_skills()

    def load_skill(self, skill_name: str) -> Skill:
        """从 .py 文件加载技能定义"""

    def list_skills(self) -> list[str]:
        """列出所有可用技能"""

    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """获取技能实例"""
```

### LoadSkillTool（agent/tools/builtin/load_skill.py）

```python
class LoadSkillTool(Tool):
    name = "load_skill"
    description = "Load a skill's full instructions by name..."

    def __init__(self, skill_loader):
        self.skill_loader = skill_loader

    def execute(self, skill_name: str) -> ToolResult:
        """返回技能的完整内容"""
```

### 技能目录结构

```
agent/skills/
├── __init__.py
├── loader.py
├── commit.py           # 技能包装器
├── commit/
│   └── SKILL.md        # 技能内容（Markdown + YAML frontmatter）
├── review-pr.py
├── review-pr/
│   └── SKILL.md
├── test.py
├── test/
│   └── SKILL.md
├── deploy.py
└── deploy/
    └── SKILL.md
```

### 技能内容格式

每个技能的 `SKILL.md` 包含 YAML frontmatter：

```markdown
---
name: commit
description: Git commit best practices following Conventional Commits
---

# Git Commit Skill

## Guidelines
...
```

### Layer 1 注入（agent/core/loop.py）

```python
def _build_skill_context(self) -> str:
    """Build Layer 1 context: skill names and short descriptions."""
    if not self._skill_loader:
        return ""
    lines = ["\n## Available Skills:"]
    for name in self._skill_loader.list_skills():
        skill = self._skill_loader.get_skill(name)
        lines.append(f"- {name}: {skill.description}")
    return "\n".join(lines)
```

## 集成

### dispatch.py 注册 LoadSkillTool

```python
if skill_loader:
    from agent.tools.builtin.load_skill import LoadSkillTool
    dispatch.register(LoadSkillTool(skill_loader))
```

### main.py 初始化

```python
skill_loader = SkillLoader(skills_dir="agent/skills")
dispatch = DispatchMap.from_directory("agent/tools/builtin", subagent_manager, skill_loader)
tools = dispatch.list_tools()

agent = Agent(..., skill_loader=skill_loader)
```

## 验证

```bash
python -c "from agent.core.skills import SkillLoader; sl = SkillLoader('agent/skills'); print(sl.list_skills())"
# Output: ['commit', 'deploy', 'review-pr', 'test']

python main.py
# Try: "What skills are available?"
# Try: "Load the commit skill"
```
