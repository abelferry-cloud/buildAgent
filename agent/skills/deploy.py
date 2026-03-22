"""Deploy skill definition."""

import os
from agent.core.skills import Skill

skill_dir = os.path.dirname(os.path.abspath(__file__))
skill_md_path = os.path.join(skill_dir, "deploy", "SKILL.md")

with open(skill_md_path, "r", encoding="utf-8") as f:
    instructions = f.read()

skill = Skill(
    name="deploy",
    description="Deployment workflow and best practices",
    instructions=instructions,
)
