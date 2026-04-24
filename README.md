# GigaAcademy Mentees Tracker

Week 5 assignment — a Python command-line tool that manages GigaAcademy mentees
in a PostgreSQL database running in Docker.

**Level completed:** Level 1 (full CRUD + interactive menu)

## Prerequisites

- Docker Desktop — `docker --version`
- Python 3.11 or newer — `python --version`

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/giga-mentees-crud.git
cd giga-mentees-crud

# 2. Copy the env template and fill in your values
cp .env.example .env

# 3. Start the PostgreSQL container (creates the mentees table automatically)
docker compose up -d

# 4. Create a virtual environment and install dependencies
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux
pip install -r requirements.txt

# 5. (Optional) Load sample mentees
docker exec -i giga_mentees_db psql -U giga -d giga_mentees < sql/seed.sql

# 6. Run the app
python app.py
```

## How to run

```bash
python app.py
```

The interactive menu will appear:

```
GigaAcademy Mentees Tracker
  1) Add mentee
  2) List mentees
  3) Update cohort
  4) Delete mentee
  0) Quit
```

## Stopping the database

```bash
docker compose down        # stop the container, keep your data
docker compose down -v     # wipe everything and start fresh
```

## What was hard

The hardest part was understanding why `conn.commit()` is necessary — at first
it seemed like the data was saving but then it would disappear. Learning that
psycopg wraps everything in a transaction by default, and that `with conn:` 
commits automatically on success, made it click.

Parameterised queries (`%s` placeholders) also took some getting used to. It
felt strange not to use f-strings, but understanding SQL injection made it clear
why this rule is non-negotiable.

Getting Docker and the Python connection to talk to each other on the right port
(5433, not the default 5432) required careful reading of the docker-compose.yml.
