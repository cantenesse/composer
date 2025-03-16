import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from typer import Option
from composer.gmail import get_sent_mail
from composer.embeddings import generate_embeddings
from composer.database import store_email
from composer.data_types import SentMail
from typing import List

app = typer.Typer()

@app.command()
def get_email(
    username: str = Option(
        ...,
        "--username", "-u",
        prompt=True,
        help="Your Gmail username"
    ),
    password: str = Option(
        ...,
        "--password", "-p",
        prompt=True,
        hide_input=True,
        confirmation_prompt=True,
        help="Your Gmail password"
    )
):
    """
    Connect to a Google account and retrieve sent emails.

    Usage:
    uv run main get-email --username your_email@gmail.com --password your_password
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        # Create a task for fetching emails
        fetching_task = progress.add_task("Fetching emails...", total=None)
        # Get sent emails from Gmail
        sent_emails = get_sent_mail(username, password)
        # Mark the fetching task as completed
        progress.update(fetching_task, completed=True)
        
        processed_emails: List[SentMail] = []
        
        # Create a task for processing emails
        if sent_emails:
            processing_task = progress.add_task("Processing emails...", total=len(sent_emails))
            for email in sent_emails:
                email_with_embeddings = generate_embeddings(email)
                processed_emails.append(email_with_embeddings)
                progress.update(processing_task, advance=1)
        else:
            typer.echo("No emails to process.")

    # Store emails in the PostgreSQL database
    store_email(processed_emails)

def main():
    app()

if __name__ == "__main__":
    main()

# Usage example:
# uv run main get-email --username <email_address> --password <password>
