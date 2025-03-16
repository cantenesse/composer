import os
import psycopg2
from psycopg2.extras import execute_values
from src.composer.data_types import SentMail
from typing import List

def store_email(sent_emails: List[SentMail]) -> bool:
    # Get database configuration from environment variables
    PG_USER = os.getenv('PG_USER')
    PG_PASSWORD = os.getenv('PG_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')
    DB_HOST = os.getenv('DB_HOST')

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=PG_USER,
        password=PG_PASSWORD,
        host=DB_HOST
    )
    cursor = conn.cursor()

    # Create the 'email' table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email (
            id TEXT PRIMARY KEY,
            recipients TEXT[],
            date TEXT,
            subject TEXT,
            message TEXT,
            embeddings REAL[]
        )
    """)
    conn.commit()

    # Overwrite existing data in the 'email' table
    cursor.execute("DELETE FROM email")

    # Prepare data for insertion
    data = [
        (
            email.id,
            email.recipients,
            email.date,
            email.subject,
            email.message,
            email.embeddings
        )
        for email in sent_emails
    ]

    # Insert data into the 'email' table
    insert_query = """
        INSERT INTO email (id, recipients, date, subject, message, embeddings)
        VALUES %s
        ON CONFLICT (id) DO UPDATE SET
            recipients = EXCLUDED.recipients,
            date = EXCLUDED.date,
            subject = EXCLUDED.subject,
            message = EXCLUDED.message,
            embeddings = EXCLUDED.embeddings
    """
    execute_values(cursor, insert_query, data)
    conn.commit()

    # Close the database connection
    cursor.close()
    conn.close()

    return True
