"""Review PR skill definition."""

import os
from agent.core.skills import Skill

skill_dir = os.path.dirname(os.path.abspath(__file__))
skill_md_path = os.path.join(skill_dir, "review-pr", "SKILL.md")

with open(skill_md_path, "r", encoding="utf-8") as f:
    instructions = f.read()

skill = Skill(
    name="review-pr",
    description="Code review best practices for pull requests",
    instructions=instructions,
)
