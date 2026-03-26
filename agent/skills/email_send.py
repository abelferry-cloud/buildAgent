"""Email sending skill using SMTP."""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from agent.tools.base import Tool, ToolResult


class EmailSendTool(Tool):
    """Send an email via SMTP."""

    name = "email_send"
    description = "Send an email message."

    def __init__(self):
        super().__init__()
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.username = os.getenv("SMTP_USERNAME", "")
        self.password = os.getenv("SMTP_PASSWORD", "")

    def execute(
        self,
        to: str,
        subject: str,
        body: str,
        is_html: bool = False,
    ) -> ToolResult:
        """Send an email."""
        if not self.username or not self.password:
            return ToolResult(
                output="",
                error="SMTP credentials not configured. Set SMTP_USERNAME and SMTP_PASSWORD."
            )

        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html' if is_html else 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            return ToolResult(output=f"邮件已发送至: {to}")
        except Exception as e:
            return ToolResult(output="", error=str(e))
