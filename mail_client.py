import email
import imaplib
import re
from email.utils import parseaddr
from bs4 import BeautifulSoup
import pandas as pd
from typing import Optional, Callable
from oauth2 import get_user_email


class MailAnalyzer:
    def __init__(self, credentials):
        self.credentials = credentials
        self.email_address = get_user_email(credentials)  # Usa API UserInfo (100% confiável)

        if not self.email_address:
            raise Exception("Não foi possível obter o email da conta autenticada!")

        self.bin_folder = None

    def connect(self):
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        auth_string = f"user={self.email_address}\1auth=Bearer {self.credentials.token}\1\1"
        typ, data = mail.authenticate("XOAUTH2", lambda x: auth_string.encode("utf-8"))
        if typ != "OK":
            raise Exception(f"XOAUTH2 authentication failed: {data}")
        return mail

    def fetch_bin_folder(self):
        mail = self.connect()
        _, folders = mail.list()
        for folder in folders:
            folder_name = folder.decode().split(' "/" ')[-1].strip('"')
            if folder_name in ["[Gmail]/Trash", "Trash"]:
                self.bin_folder = folder_name
                break
        mail.logout()

    def get_sender_statistics(self, progress_callback: Optional[Callable[[int, int], None]] = None) -> pd.DataFrame:
        mail = self.connect()
        mail.select("INBOX")

        result, messages = mail.search(None, "ALL")
        message_ids = messages[0].split()
        total_messages = len(message_ids)

        sender_data = {}

        for index, msg_id in enumerate(message_ids):
            _, msg_data = mail.fetch(msg_id, "(RFC822)")
            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)

            sender = email_message["from"]
            sender_name, sender_addr = parseaddr(sender)

            if sender_addr:
                if sender_addr not in sender_data:
                    sender_data[sender_addr] = {
                        "Sender Name": sender_name,
                        "Email": sender_addr,
                        "Count": 0,
                        "Unsubscribe Link": self.get_unsubscribe_link(raw_email)
                    }
                sender_data[sender_addr]["Count"] += 1

            if progress_callback:
                progress_callback(index + 1, total_messages)

        mail.logout()

        if not sender_data:
            return pd.DataFrame()

        return pd.DataFrame(sender_data.values()).sort_values("Count", ascending=False)

    @staticmethod
    def get_unsubscribe_link(raw_email_data) -> Optional[str]:
        email_message = email.message_from_bytes(raw_email_data)

        list_unsubscribe = email_message.get("List-Unsubscribe")
        if list_unsubscribe:
            urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', list_unsubscribe)
            if urls:
                return urls[0]

        for part in email_message.walk():
            if part.get_content_type() == "text/html":
                try:
                    html_body = part.get_payload(decode=True).decode()
                    soup = BeautifulSoup(html_body, "html.parser")

                    for a_tag in soup.find_all("a", string=re.compile("unsubscribe", re.IGNORECASE)):
                        return a_tag.get("href")

                    unsubscribe_patterns = [
                        r'https?://[^\s<>"]+(?:unsubscribe|opt[_-]out)[^\s<>"]*',
                        r'https?://[^\s<>"]+(?:click\.notification)[^\s<>"]*',
                    ]
                    for pattern in unsubscribe_patterns:
                        matches = re.findall(pattern, html_body, re.IGNORECASE)
                        if matches:
                            return matches[0]
                except Exception:
                    pass

        return None

    def delete_emails_from_sender(self, sender_email: str) -> int:
        mail = self.connect()
        mail.select("INBOX", readonly=False)

        result, messages = mail.search(None, f'FROM "{sender_email}"')
        message_ids = messages[0].split()

        if not message_ids:
            return 0

        if self.bin_folder is None:
            self.fetch_bin_folder()

        for msg_id in message_ids:
            mail.copy(msg_id, self.bin_folder)

        mail.logout()
        return len(message_ids)
