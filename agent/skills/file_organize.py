"""File organization skill."""

import os
import shutil
from pathlib import Path
from typing import Optional

from agent.tools.base import Tool, ToolResult


class FileOrganizeTool(Tool):
    """Organize files in a directory."""

    name = "file_organize"
    description = "Organize files in a directory by type or date."

    def execute(
        self,
        source_dir: str,
        mode: str = "by_extension",
        target_dir: Optional[str] = None,
    ) -> ToolResult:
        """Organize files in source directory."""
        source = Path(source_dir)
        target = Path(target_dir) if target_dir else source

        if not source.exists():
            return ToolResult(output="", error=f"Source directory not found: {source_dir}")

        try:
            organized = []
            for file in source.iterdir():
                if file.is_file():
                    if mode == "by_extension":
                        ext = file.suffix.lstrip(".").lower() or "no_extension"
                        dest_dir = target / ext.upper()
                        dest_dir.mkdir(exist_ok=True)
                        shutil.move(str(file), str(dest_dir / file.name))
                        organized.append(f"{file.name} -> {ext.upper()}/")

            return ToolResult(output=f"已整理 {len(organized)} 个文件:\n" + "\n".join(organized))
        except Exception as e:
            return ToolResult(output="", error=str(e))
