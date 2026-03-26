"""Document Agent - handles document generation (PPT, Word, Excel)."""

from agent.skills.ppt_generate import PptGenerateTool
from agent.skills.docx_generate import DocxGenerateTool
from agent.skills.excel_generate import ExcelGenerateTool


class DocumentAgent:
    """Agent specialized in document generation."""

    def __init__(self):
        self.ppt_tool = PptGenerateTool()
        self.docx_tool = DocxGenerateTool()
        self.excel_tool = ExcelGenerateTool()

    async def generate_ppt(self, title: str, slides: list[dict], output_filename: str) -> str:
        """Generate a PowerPoint presentation."""
        result = self.ppt_tool.execute(title=title, slides=slides, output_filename=output_filename)
        return result.output if not result.error else f"生成失败: {result.error}"

    async def generate_docx(self, title: str, paragraphs: list[str], output_filename: str) -> str:
        """Generate a Word document."""
        result = self.docx_tool.execute(title=title, paragraphs=paragraphs, output_filename=output_filename)
        return result.output if not result.error else f"生成失败: {result.error}"

    async def generate_excel(self, headers: list[str], rows: list[list[str]], sheet_name: str, output_filename: str) -> str:
        """Generate an Excel spreadsheet."""
        result = self.excel_tool.execute(
            headers=headers, rows=rows, sheet_name=sheet_name, output_filename=output_filename
        )
        return result.output if not result.error else f"生成失败: {result.error}"
