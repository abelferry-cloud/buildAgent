# s05: Skills - 实现效果

## 核心功能

### SkillLoader（agent/skills/loader.py）

```python
class SkillLoader:
    """运行时技能加载，支持热重载"""

    def __init__(self, skills_dir: str = "agent/skills"):
        self.skills_dir = skills_dir
        self._skills: dict[str, dict] = {}

    def load_skill(self, name: str) -> dict:
        """按需加载技能完整内容"""
        if name not in self._skills:
            self._skills[name] = self._load_skill_file(name)
        return self._skills[name]

    def list_skills(self) -> list[str]:
        """列出可用技能"""
        return list(self._skills.keys())
```

## 待实现

### 两层注入架构

| 层级 | 时机 | 内容 |
|------|------|------|
| Layer 1 | 系统提示 | 技能名称 + 简短描述 (~100 tokens) |
| Layer 2 | tool_result | 按需加载完整内容 (~2000 tokens) |

### 技能目录结构

```
agent/skills/
├── commit/
│   └── SKILL.md      # YAML frontmatter + 内容
├── review-pr/
│   └── SKILL.md
└── test/
    └── SKILL.md
```
