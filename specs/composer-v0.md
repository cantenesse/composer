# Composer v0 Specification

## High-Level Objective

- Create a CLI that gets sent mail from Gmail account and populates a postgres table

## Mid-Level Objective

- Build a python MVP CLI 
- The user will provide credentials for a Google account 
- The CLI will connect to Gmail, read what the user's sent mail, and save it in a local postgres database

## Implementation Notes
- No need to import any external libraries see pyproject.toml for dependencies.
- Comment every function.
- For typer commands add usage examples starting with `uv run main <func name dash sep and params>`
- When code block is given in low-level tasks, use it without making changes.
- Carefully review each low-level task for exact code changes.

## Context

### Beginning context
- `pyproject.toml` (readonly)

### Ending context  
- `src/composer/main.py`
- `src/composer/embeddings.py`
- `src/composer/data_types.py`
- `src/composer/gmail.py`
- `src/composer/database.py`

## Low-Level Tasks
> Ordered from start to finish

1. Create CLI that accepts a string which represents a Google account address and password
```aider
CREATE /src/composer/main.py: 
    CREATE imports and necessary code to make this a typer CLI 
    CREATE main() that simple invokes app()
```

2. Create our data types
```aider
CREATE src/composer/data_types.py:
    CREATE pydantic type:

        SentMail(BaseModel): {
            id: str
            recipients: List[str]
            date: str
            subject: str
            message: str
            embeddings: List[float]
        }

```

3. Create a function that connects to a Google account and reads sent mail
```aider
CREATE src/composer/gmail.py
    CREATE get_sent_mail(username: str, password: str) -> List[SentMail]:
        Connect to a Google account. Get all sent mail. Return a list of all sent messages. For 'embeddings', create an empty list.
        The account may require 2FA authentication. If so, support prompting the user for the 2FA method.

```

4. Create a function that creates embeddings for each item of SentEmail 
```aider
CREATE src/composer/embeddings.py:
    CREATE generate_embeddings(sent_email: SentEmail) -> List[SentMail]
        This should generate embeddings for SentEmail.message and store it in SentEmail.embeddings.
        Use sentance-transformers to create the embeddings.


```

5. Create a function that stores SentEmail in a postgres database
```aider
CREATE src/composer/database.py:
    CREATE store_email(sent_emails: List[SentEmail]) -> bool
        This should interact with a postgres database that is configured using environment varialbes.
        The environment variables are PG_USER for username, PG_PASSWORD for password, DB_NAME for database name, and DB_HOST for the hostname.
        The query should overwrite whatever is in the table. The table name is email
        The field names correspond to the SentMail data type. The id should be a uuid. recipipients, date, subject, and message should come from the gmail integration. And embeddings should come from `generate_embeddings` function

```
    

6. Update main function to use database and analyze_invoice functions
```aider
UPDATE src/composer/main.py:
    CREATE a new typer cli application:
        CREATE app.command() def get_email():
            Use get_sent_mail() to connect to the Google account and get the sent email.
            Loop through each email and create embeddings.
            Store each email in SentEmail in a row in the email table.
``` 