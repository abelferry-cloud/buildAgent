"""Email reading skill using IMAP."""

import imaplib
import email
import os
from typing import Optional

from agent.tools.base import Tool, ToolResult


class EmailReadTool(Tool):
    """Read emails from an IMAP mailbox."""

    name = "email_read"
    description = "Read recent emails from mailbox."

    def __init__(self):
        super().__init__()
        self.imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
        self.username = os.getenv("IMAP_USERNAME", "")
        self.password = os.getenv("IMAP_PASSWORD", "")

    def execute(self, mailbox: str = "INBOX", max_results: int = 10) -> ToolResult:
        """Read recent emails."""
        if not self.username or not self.password:
            return ToolResult(
                output="",
                error="IMAP credentials not configured. Set IMAP_USERNAME and IMAP_PASSWORD."
            )

        try:
            with imaplib.IMAP4_SSL(self.imap_server) as mail:
                mail.login(self.username, self.password)
                mail.select(mailbox)

                _, messages = mail.search(None, "ALL")
                email_ids = messages[0].split()[-max_results:]

                results = []
                for eid in email_ids:
                    _, data = mail.fetch(eid, "(RFC822)")
                    msg = email.message_from_bytes(data[0][1])
                    results.append({
                        "from": msg["from"],
                        "subject": msg["subject"],
                        "date": msg["date"],
                    })

                formatted = [f"- From: {r['from']}\n  Subject: {r['subject']}\n  Date: {r['date']}" for r in results]
                return ToolResult(output="\n".join(formatted) if formatted else "No emails found.")
        except Exception as e:
            return ToolResult(output="", error=str(e))
