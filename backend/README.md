# Backend

## Install Poetry

Use [Poetry](https://python-poetry.org/) for dependency management.

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
```

Or follow installation instructions from [Poetry website](https://python-poetry.org/docs/#installation).

## Setup Virtual Environment

It is recommended to use Python virtual environment, so you don't pollute your system Python environment.

```bash
# Install dependencies
poetry install
```

```bash
# Update/upgrade dependencies
poetry update
```

```bash
# Activate Python virtual environment
poetry shell
```

## Environment Variables
Copy an existing environment template file and fill in all the necessary values:
```bash
# Create .env file (by copying from .env.example)
cp .env.example .env
```

## Set up Supabase

1. Create a project (Note down your project's password)
2. Click on the `Connect` button
3. Copy the URI
4. Run `psql "<COPIED URI>"` (Remember to put the password in)
5. Run `\i ./supabase_schema.sql`
6. You are done!

### Start the server (locally)

```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```


## Dockerfile - Building and running the docker image

```
#Build the docker image
docker build --no-cache -t backend -f docker/development/Dockerfile .

#Run the docker image
docker run -it -p 8080:8080 --env-file .env backend
```

### Check style

Run the following command at the root of `backend` directory
`black .`
`isort .`