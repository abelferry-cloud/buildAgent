"""File Agent - handles file operations and organization."""

from agent.skills.file_organize import FileOrganizeTool


class FileAgent:
    """Agent specialized in file management."""

    def __init__(self):
        self.organize_tool = FileOrganizeTool()

    async def organize_files(self, source_dir: str, mode: str = "by_extension", target_dir: str = None) -> str:
        """Organize files in a directory."""
        result = self.organize_tool.execute(source_dir=source_dir, mode=mode, target_dir=target_dir)
        return result.output if not result.error else f"整理失败: {result.error}"
