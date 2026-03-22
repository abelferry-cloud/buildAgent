"""s05: Skills - Tests for SkillLoader and two-layer skill injection."""

import pytest
import os
import tempfile
import shutil


class TestSkill:
    """Tests for Skill dataclass."""

    def test_skill_creation(self):
        """Test creating a skill."""
        from agent.core.skills import Skill
        skill = Skill(
            name="test-skill",
            description="A test skill",
            instructions="Do the thing"
        )
        assert skill.name == "test-skill"
        assert skill.description == "A test skill"
        assert skill.tools == []

    def test_skill_with_tools(self):
        """Test skill with associated tools."""
        from agent.core.skills import Skill
        from agent.tools.base import Tool, ToolResult

        class TestTool(Tool):
            name = "test"
            description = "Test tool"
            def execute(self, **kwargs):
                return ToolResult(tool_call_id="", output="")

        skill = Skill(
            name="test-skill",
            description="A test skill",
            instructions="Instructions",
            tools=[TestTool()]
        )
        assert len(skill.tools) == 1
        assert skill.tools[0].name == "test"

    def test_skill_get_aliases(self):
        """Test getting skill aliases."""
        from agent.core.skills import Skill
        skill = Skill(
            name="test-skill",
            description="A test skill",
            instructions="Instructions",
            aliases=["alias1", "alias2"]
        )
        aliases = skill.get_aliases()
        assert "test-skill" in aliases
        assert "alias1" in aliases
        assert "alias2" in aliases


class TestSkillLoader:
    """Tests for SkillLoader class."""

    def test_skill_loader_initialization(self, tmp_path):
        """Test SkillLoader initialization."""
        from agent.core.skills import SkillLoader

        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        loader = SkillLoader(skills_dir=str(skills_dir))
        assert loader is not None

    def test_list_skills_empty(self, tmp_path):
        """Test listing skills when none exist."""
        from agent.core.skills import SkillLoader

        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        loader = SkillLoader(skills_dir=str(skills_dir))
        skills = loader.list_skills()
        assert isinstance(skills, list)

    def test_get_skill_not_found(self, tmp_path):
        """Test getting a skill that doesn't exist."""
        from agent.core.skills import SkillLoader

        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        loader = SkillLoader(skills_dir=str(skills_dir))
        skill = loader.get_skill("nonexistent")
        assert skill is None

    def test_load_skill_file_not_found(self, tmp_path):
        """Test loading a skill that doesn't exist as a file."""
        from agent.core.skills import SkillLoader

        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        loader = SkillLoader(skills_dir=str(skills_dir))
        with pytest.raises(FileNotFoundError):
            loader.load_skill("nonexistent")


class TestSkillIntegration:
    """
    Integration tests based on TODO prompts.

    TODO prompts:
    - What skills are available?
    - Load the agent-builder skill and follow its instructions
    - I need to do a code review -- load the relevant skill first
    - Build an MCP server using the mcp-builder skill
    """

    def test_list_available_skills(self, tmp_path):
        """Test listing available skills in the system."""
        from agent.core.skills import SkillLoader

        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        # Create a real skill file
        skill_file = skills_dir / "commit.py"
        skill_file.write_text('''"""Commit skill."""

from agent.core.skills import Skill

skill = Skill(
    name="commit",
    description="Git commit best practices",
    instructions="Follow conventional commits format"
)
''')

        loader = SkillLoader(skills_dir=str(skills_dir))
        skills = loader.list_skills()
        assert "commit" in skills

    def test_load_code_review_skill(self, tmp_path):
        """Test loading the code review skill."""
        from agent.core.skills import SkillLoader

        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        # Create a skill file - filename determines skill name
        skill_file = skills_dir / "review_pr.py"
        skill_file.write_text('''"""Review PR skill."""

from agent.core.skills import Skill

skill = Skill(
    name="review_pr",
    description="Code review skill",
    instructions="Steps:\\n1. Read PR\\n2. Check code\\n3. Provide feedback"
)
''')

        loader = SkillLoader(skills_dir=str(skills_dir))
        # Skill name is derived from filename (without .py)
        skill = loader.get_skill("review_pr")
        assert skill is not None
        assert "review" in skill.description.lower()

    def test_layer_one_vs_layer_two_injection(self, tmp_path):
        """Test the two-layer skill injection mechanism."""
        from agent.core.skills import SkillLoader, Skill

        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        # Create a skill with detailed content
        skill_file = skills_dir / "test_skill.py"
        skill_file.write_text('''"""Test skill."""

from agent.core.skills import Skill

skill = Skill(
    name="test_skill",
    description="Short description",
    instructions="Full detailed instructions that are loaded when needed (Layer 2)"
)
''')

        loader = SkillLoader(skills_dir=str(skills_dir))

        # Layer 1: Just name and brief description
        skill = loader.get_skill("test_skill")
        assert skill is not None
        assert len(skill.description) < 200

        # Layer 2: Full content is in instructions
        assert len(skill.instructions) > 0

    def test_inject_tools(self, tmp_path):
        """Test injecting skill tools into base tools."""
        from agent.core.skills import SkillLoader, Skill
        from agent.tools.base import Tool, ToolResult

        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        class BashTool(Tool):
            name = "bash"
            description = "Run bash"
            def execute(self, **kwargs):
                return ToolResult(tool_call_id="", output="")

        class GitTool(Tool):
            name = "git"
            description = "Git operations"
            def execute(self, **kwargs):
                return ToolResult(tool_call_id="", output="")

        skill_file = skills_dir / "commit.py"
        skill_file.write_text('''"""Commit skill."""

from agent.core.skills import Skill
from agent.tools.base import Tool, ToolResult

class CommitTool(Tool):
    name = "commit"
    description = "Create a commit"
    def execute(self, **kwargs):
        return ToolResult(tool_call_id="", output="")

skill = Skill(
    name="commit",
    description="Git commit skill",
    instructions="Use conventional commits",
    tools=[CommitTool()]
)
''')

        loader = SkillLoader(skills_dir=str(skills_dir))

        # Layer 1: Skills are registered
        skills = loader.list_skills()
        assert "commit" in skills

        # Layer 2: Skill's tools can be injected
        skill = loader.get_skill("commit")
        assert len(skill.tools) == 1


class TestLoadSkillTool:
    """Tests for the load_skill tool."""

    def test_load_skill_tool_exists(self):
        """Test that LoadSkillTool class exists."""
        from agent.tools.builtin.load_skill import LoadSkillTool
        assert LoadSkillTool is not None
