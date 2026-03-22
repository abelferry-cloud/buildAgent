"""s05: Skill System - Skill definitions and loader."""

import os
from dataclasses import dataclass, field
from typing import Optional

from agent.tools.base import Tool


@dataclass
class Skill:
    """
    A skill definition with instructions and associated tools.

    Skills provide a way to bundle instructions + tools for reuse.
    They support two-layer injection: tools + context.
    """

    name: str
    description: str
    instructions: str
    tools: list[Tool] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def get_aliases(self) -> list[str]:
        """Get all aliases for this skill including the main name."""
        return [self.name] + self.aliases


class SkillLoader:
    """
    Loads and manages skill definitions.

    Two-layer injection:
    1. Tools: Which tools this skill provides
    2. Context: Additional context/instructions to inject

    Skills are loaded from files and can be composed with base tools.
    """

    def __init__(self, skills_dir: str):
        """
        Initialize the SkillLoader.

        Args:
            skills_dir: Directory containing skill definition files
        """
        self.skills_dir = skills_dir
        self._skills: dict[str, Skill] = {}
        self._load_all_skills()

    def _load_all_skills(self) -> None:
        """Load all skill definitions from the skills directory."""
        if not os.path.exists(self.skills_dir):
            return

        for filename in os.listdir(self.skills_dir):
            if filename.endswith(".py") and filename not in ("__init__.py", "loader.py"):
                skill_name = filename[:-3]
                try:
                    self.load_skill(skill_name)
                except (FileNotFoundError, ValueError):
                    pass  # Skip files that aren't valid skill definitions

    def load_skill(self, skill_name: str) -> Skill:
        """
        Load a skill by name.

        Args:
            skill_name: Name of the skill to load

        Returns:
            The loaded Skill instance

        Raises:
            FileNotFoundError: If skill definition file not found
            ValueError: If skill definition is invalid
        """
        skill_path = os.path.join(self.skills_dir, f"{skill_name}.py")
        if not os.path.exists(skill_path):
            raise FileNotFoundError(f"Skill '{skill_name}' not found at {skill_path}")

        # Load skill from file - expects a 'skill' object in the module
        import importlib.util
        spec = importlib.util.spec_from_file_location(skill_name, skill_path)
        if spec is None or spec.loader is None:
            raise ValueError(f"Could not load skill '{skill_name}'")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, "skill"):
            raise ValueError(f"Skill '{skill_name}' does not define a 'skill' object")

        skill = module.skill
        if not isinstance(skill, Skill):
            raise ValueError(f"Skill '{skill_name}' must be a Skill instance")

        self._skills[skill_name] = skill
        return skill

    def list_skills(self) -> list[str]:
        """
        List all available skill names.

        Returns:
            List of loaded skill names
        """
        return list(self._skills.keys())

    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """Get a skill by name."""
        return self._skills.get(skill_name)

    def inject_tools(self, skill: Skill, base_tools: list[Tool]) -> list[Tool]:
        """
        Inject skill's tools into the base tools list.

        This implements the two-layer injection:
        - Layer 1: Skill's own tools are added
        - Layer 2: Context from skill instructions is made available

        Args:
            skill: The skill to inject tools from
            base_tools: Base list of tools to extend

        Returns:
            Combined list of base tools + skill tools
        """
        # Create a map of base tools by name for deduplication
        tool_map = {t.name: t for t in base_tools}

        # Add skill's tools (they override base tools with same name)
        for tool in skill.tools:
            tool_map[tool.name] = tool

        return list(tool_map.values())

    def inject_context(self, skill: Skill, system_prompt: str) -> str:
        """
        Inject skill context into a system prompt.

        Args:
            skill: The skill to extract context from
            system_prompt: Base system prompt

        Returns:
            System prompt with skill context appended
        """
        if not skill.instructions:
            return system_prompt

        context_block = f"\n\n# Skill: {skill.name}\n{skill.instructions}"
        return system_prompt + context_block
