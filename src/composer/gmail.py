import imaplib
import email
import chardet
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

                    # Initialize variables with default values
                    subject = "(No Subject)"
                    date = "(No Date)"
                    recipients = []
                    message = ""

                    # Decode email fields
                    subject_raw = msg["Subject"]
                    if subject_raw is not None:
                        subject_tuple = decode_header(subject_raw)[0]
                        subject_content, encoding = subject_tuple
                        if isinstance(subject_content, bytes):
                            subject = subject_content.decode(encoding if encoding else "utf-8", errors='replace')
                        else:
                            subject = subject_content

                    date = msg["Date"] if msg["Date"] is not None else "(No Date)"
                    recipients = msg.get_all("To", [])

                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                payload = part.get_payload(decode=True)
                                if payload is not None:
                                    charset = part.get_content_charset()
                                    if not charset:
                                        # Detect encoding if charset is not specified
                                        result = chardet.detect(payload)
                                        charset = result['encoding'] if result['encoding'] else 'utf-8'
                                    try:
                                        message = payload.decode(charset, errors='replace')
                                    except (UnicodeDecodeError, LookupError):
                                        message = payload.decode('utf-8', errors='replace')
                                else:
                                    # If payload is None, set message to empty string
                                    message = ""
                                break
                    else:
                        payload = msg.get_payload(decode=True)
                        if payload is not None:
                            charset = msg.get_content_charset()
                            if not charset:
                                # Detect encoding if charset is not specified
                                result = chardet.detect(payload)
                                charset = result['encoding'] if result['encoding'] else 'utf-8'
                            try:
                                message = payload.decode(charset, errors='replace')
                            except (UnicodeDecodeError, LookupError):
                                message = payload.decode('utf-8', errors='replace')
                        else:
                            # If payload is None, set message to empty string
                            message = ""

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
