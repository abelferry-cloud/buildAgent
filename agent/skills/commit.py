"""Commit skill definition."""

import os
from agent.core.skills import Skill

skill_dir = os.path.dirname(os.path.abspath(__file__))
skill_md_path = os.path.join(skill_dir, "commit", "SKILL.md")

with open(skill_md_path, "r", encoding="utf-8") as f:
    instructions = f.read()

skill = Skill(
    name="commit",
    description="Git commit best practices following Conventional Commits",
    instructions=instructions,
)
