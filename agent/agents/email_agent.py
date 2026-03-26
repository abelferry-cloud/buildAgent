"""Email Agent - handles email sending and reading."""

from agent.skills.email_send import EmailSendTool
from agent.skills.email_read import EmailReadTool


class EmailAgent:
    """Agent specialized in email management."""

    def __init__(self):
        self.send_tool = EmailSendTool()
        self.read_tool = EmailReadTool()

    async def send_email(self, to: str, subject: str, body: str, is_html: bool = False) -> str:
        """Send an email."""
        result = self.send_tool.execute(to=to, subject=subject, body=body, is_html=is_html)
        return result.output if not result.error else f"发送失败: {result.error}"

    async def read_emails(self, mailbox: str = "INBOX", max_results: int = 10) -> str:
        """Read recent emails."""
        result = self.read_tool.execute(mailbox=mailbox, max_results=max_results)
        return result.output if not result.error else f"读取失败: {result.error}"
