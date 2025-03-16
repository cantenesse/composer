import imaplib
import email
from email.header import decode_header
from typing import List
from composer.data_types import SentMail

def get_sent_mail(username: str, password: str) -> List[SentMail]:
    # Connect to the Gmail IMAP server
    imap = imaplib.IMAP4_SSL("imap.gmail.com")

    try:
        # Login to the account
        imap.login(username, password)
    except imaplib.IMAP4.error:
        print("Login failed. Please check your username and password.")
        return []

    # Select the 'Sent Mail' folder
    imap.select('"[Gmail]/Sent Mail"')

    # Search for all emails in the 'Sent Mail' folder
    status, messages = imap.search(None, "ALL")

    email_list = []

    if status == "OK":
        for num in messages[0].split():
            # Fetch the email by ID
            status, msg_data = imap.fetch(num, "(RFC822)")
            if status != "OK":
                print("Failed to fetch email.")
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    # Parse the email
                    msg = email.message_from_bytes(response_part[1])

                    # Decode email fields
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    date = msg["Date"]
                    recipients = msg.get_all("To", [])
                    message = ""

                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                message = part.get_payload(decode=True).decode()
                                break
                    else:
                        message = msg.get_payload(decode=True).decode()

                    # Create SentMail object
                    email_obj = SentMail(
                        id=num.decode(),
                        recipients=recipients,
                        date=date,
                        subject=subject,
                        message=message,
                        embeddings=[]
                    )
                    email_list.append(email_obj)
    else:
        print("No emails found.")

    # Logout and close the connection
    imap.logout()

    return email_list
