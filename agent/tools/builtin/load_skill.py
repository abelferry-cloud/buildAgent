"""s05: LoadSkillTool - Load a skill's full instructions on demand."""

from agent.tools.base import Tool, ToolResult


class LoadSkillTool(Tool):
    """
    Tool to load a skill's full instructions.

    This implements Layer 2 of the two-layer skill injection:
    - Layer 1: Skill names + descriptions in system prompt (~100 tokens)
    - Layer 2: Full skill content loaded via this tool (~2000 tokens)

    The LLM can call this tool when it needs detailed guidance
    from a specific skill.
    """

    name = "load_skill"
    description = "Load a skill's full instructions by name. Returns the complete skill content. Use this when you need detailed guidance on a specific skill like commit, review-pr, test, or deploy."

    def __init__(self, skill_loader):
        """
        Initialize LoadSkillTool with a SkillLoader.

        Args:
            skill_loader: SkillLoader instance to use for loading skills
        """
        self.skill_loader = skill_loader

    def execute(self, skill_name: str) -> ToolResult:
        """
        Load and return the full instructions for a skill.

        Args:
            skill_name: Name of the skill to load (e.g., 'commit', 'review-pr', 'test')

        Returns:
            ToolResult with the skill's full content, or error if not found
        """
        skill = self.skill_loader.get_skill(skill_name)
        if not skill:
            available = ", ".join(self.skill_loader.list_skills()) or "none"
            return ToolResult(
                tool_call_id="",
                output="",
                error=f"Skill '{skill_name}' not found. Available skills: {available}",
            )

        content = f"# {skill.name}\n\n**Description:** {skill.description}\n\n---\n\n{skill.instructions}"
        return ToolResult(tool_call_id="", output=content)
