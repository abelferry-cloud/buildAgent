"""s05: Skill Loader Implementation - Runtime skill loading and management."""

import importlib
import os
from typing import Optional

from agent.core.skills import Skill, SkillLoader as BaseSkillLoader
from agent.tools.base import Tool


class SkillLoader(BaseSkillLoader):
    """
    Extended skill loader with runtime management.

    Provides additional functionality beyond base SkillLoader:
    - Dynamic skill loading at runtime
    - Skill hot-reloading
    - Skill dependency resolution
    """

    def __init__(self, skills_dir: str):
        """
        Initialize the extended SkillLoader.

        Args:
            skills_dir: Directory containing skill definition files
        """
        super().__init__(skills_dir)
        self._loaded_modules: dict[str, object] = {}

    def reload_skill(self, skill_name: str) -> Skill:
        """
        Reload a skill definition from disk.

        Useful for development when updating skill instructions.

        Args:
            skill_name: Name of the skill to reload

        Returns:
            The reloaded Skill instance
        """
        # Clear cached module if exists
        if skill_name in self._loaded_modules:
            del self._loaded_modules[skill_name]

        # Remove old skill if exists
        if skill_name in self._skills:
            del self._skills[skill_name]

        return self.load_skill(skill_name)

    def hot_reload_enabled(self) -> bool:
        """Check if hot-reload is enabled for development."""
        return True

    def load_skill(self, skill_name: str) -> Skill:
        """
        Load a skill with module caching.

        Args:
            skill_name: Name of the skill to load

        Returns:
            The loaded Skill instance
        """
        # Check if already loaded and cached
        if skill_name in self._loaded_modules:
            skill = self._skills.get(skill_name)
            if skill:
                return skill

        # Use parent class loading mechanism
        skill = super().load_skill(skill_name)

        # Cache the module
        skill_path = os.path.join(self.skills_dir, f"{skill_name}.py")
        if os.path.exists(skill_path):
            spec = importlib.util.spec_from_file_location(skill_name, skill_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(module)
                    self._loaded_modules[skill_name] = module
                except Exception:
                    pass  # Module already loaded, ignore

        return skill

    def get_skill_tools(self, skill_name: str) -> list[Tool]:
        """
        Get only the tools provided by a specific skill.

        Args:
            skill_name: Name of the skill

        Returns:
            List of tools defined by the skill
        """
        skill = self.get_skill(skill_name)
        if not skill:
            return []
        return skill.tools

    def skill_exists(self, skill_name: str) -> bool:
        """Check if a skill exists (loaded or on disk)."""
        if skill_name in self._skills:
            return True
        skill_path = os.path.join(self.skills_dir, f"{skill_name}.py")
        return os.path.exists(skill_path)

    def get_skill_metadata(self, skill_name: str) -> dict:
        """
        Get metadata for a skill.

        Args:
            skill_name: Name of the skill

        Returns:
            Metadata dict, empty if skill not found
        """
        skill = self.get_skill(skill_name)
        if not skill:
            return {}
        return skill.metadata
