# S05: Skills - 总结

## 核心理念

> Two-layer skill injection: tools + context

## 核心原理

S05 实现了运行时技能加载系统，支持热重载。技能（Skill）是 instructions + tools 的打包单元，可以被 Agent 动态加载。

### 两层注入架构

1. **Layer 1: 工具层** - `inject_tools()` 将技能的专用工具合并到基础工具集
2. **Layer 2: 上下文层** - `inject_context()` 将技能指令附加到系统提示词

### SkillLoader 功能

- **加载技能** - 从 `agent/skills/` 目录加载技能定义
- **列出技能** - `list_skills()` 返回所有可用技能
- **获取技能** - `get_skill()` 返回指定技能详情
- **热重载** - `reload_skill()` 支持运行时重新加载技能定义

## 关键类/组件

| 名称 | 文件 | 职责 |
|------|------|------|
| `Skill` | `agent/core/skills.py` | 技能数据结构（name, description, instructions, tools） |
| `SkillLoader` | `agent/core/skills.py` | 基础技能加载器 |
| `SkillLoader` | `agent/skills/loader.py` | 扩展技能加载器，支持热重载 |

## 涉及的文件

### 核心文件
- `agent/core/skills.py` - Skill 数据结构和基础 SkillLoader
- `agent/skills/loader.py` - 扩展 SkillLoader 实现

### 工具文件
- `agent/tools/builtin/load_skill.py` - LoadSkillTool，LLM 加载技能内容的工具

## 与 main.py 的集成

```python
from agent.core.skills import SkillLoader

skill_loader = SkillLoader(skills_dir="agent/skills")

# DispatchMap 加载时需要
dispatch = DispatchMap.from_directory("agent/tools/builtin", subagent_manager, skill_loader)

# Agent 创建时注入
agent = Agent(..., skill_loader=skill_loader)
```

## Skill 数据结构

```python
@dataclass
class Skill:
    name: str
    description: str
    instructions: str  # 技能使用说明
    tools: list[Tool]  # 技能提供的工具
    aliases: list[str]  # 别名列表
    metadata: dict      # 元数据
```

## 架构图

```
┌─────────────────────────────────────┐
│           SkillLoader               │
│  ┌───────────────────────────────┐  │
│  │ _skills_dir: str              │  │
│  │ _skills: dict[str, Skill]     │  │
│  │ _hot_reload: bool = True      │  │
│  └───────────────────────────────┘  │
│  load_skill() │ list_skills() │ reload_skill()
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│     agent/skills/ 目录              │
│  ┌───────────────────────────────┐  │
│  │ skill_name/                    │  │
│  │   ├── skill.yaml              │  │
│  │   └── tools/                  │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
              │
              ▼ inject_tools() + inject_context()
┌─────────────────────────────────────┐
│         Agent System Prompt         │
└─────────────────────────────────────┘
```
