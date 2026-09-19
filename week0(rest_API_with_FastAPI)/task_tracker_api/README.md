# Task Tracker API

A lightweight RESTful API built with Python, FastAPI, and MySQL for managing tasks and comments.

## Features

- CRUD operations for tasks (create, list, get, update, delete)
- Comments attached to individual tasks
- Request/response validation via Pydantic
- Interactive OpenAPI docs at `/docs` out of the box
- Automated `pytest` test suite covering the task endpoints
- One-command local setup with Docker Compose (API + MySQL, with a healthcheck so the API waits for the DB)

## Project Structure

```
task_tracker_api/
├── app/
│   ├── __init__.py
│   ├── main.py       # FastAPI app instance
│   ├── routes.py     # API endpoints
│   ├── models.py     # Pydantic request/response models
│   └── db.py         # MySQL connection helper
├── tests/
│   ├── conftest.py    # Pytest fixtures (test DB setup/teardown, test client)
│   └── test_tasks.py  # Tests for the task endpoints
├── schema.sql          # Database schema (users, tasks, comments)
├── requirements.txt
├── Dockerfile           # Builds the API service image
├── docker-compose.yml   # Runs the API + MySQL together
└── .dockerignore
```

## Requirements

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose (recommended — see [Setup with Docker](#setup-with-docker))
- Or, for a manual setup: Python 3.11+ and MySQL 8.0+ (see [Setup without Docker](#setup-without-docker))

## Setup with Docker

This is the easiest way to run the whole stack (API + MySQL) with one command.

### 1. Clone the repository

```bash
git clone <https://github.com/wassimrayani17-arch/my-cybersecurity-roadmap.git>
cd task_tracker_api
```

### 2. Set the database password

`docker-compose.yml` reads the MySQL password from a `DB_PASSWORD` environment variable, used both to set up the MySQL user and for the API to connect to it. Set it in your terminal before starting the containers:

**Windows (cmd):**
```cmd
set DB_PASSWORD=your_password_here
```

**Windows (PowerShell):**
```powershell
$env:DB_PASSWORD='your_password_here'
```

**macOS/Linux:**
```bash
export DB_PASSWORD=your_password_here
```

This only lasts for the current terminal session — you'll need to set it again each time you open a new terminal, or put it in a `.env` file in the project root instead (Docker Compose loads it automatically):

```
DB_PASSWORD=your_password_here
```

### 3. Build and start the containers

```bash
docker compose up --build
```

This starts two services:

| Service | What it is                                                              | Port                 |
|---------|--------------------------------------------------------------------------|-----------------------|
| `db`    | MySQL 8.0, auto-initialized with `schema.sql` on first run               | `3307` → container `3306` |
| `api`   | The FastAPI app, built from the `Dockerfile`                             | `8000`                |

The `api` service waits for `db` to report healthy (via a `mysqladmin ping` healthcheck) before starting, so there's no manual waiting or connection-retry logic needed.

The API is then available at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`.

To stop the containers, press `Ctrl+C`, or run `docker compose down` from another terminal. To also wipe the MySQL data volume (start completely fresh next time), use `docker compose down -v`.

> `schema.sql` is only applied automatically the **first** time the `db` container's volume is created. If you change `schema.sql` later, run `docker compose down -v` first so MySQL re-initializes from the updated file.

### Rebuilding after code changes

The `api` image bundles the `app/` code at build time, so it doesn't hot-reload. After editing files under `app/`, rebuild that service:

```bash
docker compose up --build api
```

## Setup without Docker

If you'd rather run things directly on your machine instead of in containers:

### 1. Clone the repository

```bash
git clone <https://github.com/wassimrayani17-arch/my-cybersecurity-roadmap.git>
cd task_tracker_api
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up the database

Create a database and load the schema:

```bash
mysql -u root -p -e "CREATE DATABASE task_tracker;"
mysql -u root -p task_tracker < schema.sql
```

`schema.sql` defines three tables:

| Table      | Purpose                                              |
|------------|-------------------------------------------------------|
| `users`    | `id`, `username` (unique)                             |
| `tasks`    | `id`, `title`, `completed`, `owner_id` (FK → users)   |
| `comments` | `id`, `task_id` (FK → tasks, cascades on delete), `body` |

### 5. Set the database connection details

`app/db.py` reads its connection details from environment variables, falling back to sensible local defaults (`localhost`, `task_api`, `task_tracker`) for everything except the password, which is required:

```python
host=os.environ.get("DB_HOST", "localhost"),
user=os.environ.get("DB_USER", "task_api"),
password=os.environ["DB_PASSWORD"],
database=os.environ.get("DB_NAME", "task_tracker"),
```

At minimum, set `DB_PASSWORD` in your terminal before starting the server:

**Windows (cmd):**
```cmd
set DB_PASSWORD=your_password_here
```

**Windows (PowerShell):**
```powershell
$env:DB_PASSWORD='your_password_here'
```

**macOS/Linux:**
```bash
export DB_PASSWORD=your_password_here
```

This only lasts for the current terminal session — you'll need to set it again each time you open a new terminal to run the server. Set `DB_HOST`, `DB_USER`, or `DB_NAME` too if your local setup differs from the defaults.

### 6. Run the server

```bash
uvicorn app.main:app --reload
```

The API is then available at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`.

## API Endpoints

| Method | Path                        | Description               |
|--------|-----------------------------|-----------------------------|
| GET    | `/tasks`                    | List all tasks              |
| GET    | `/tasks/{task_id}`          | Get a single task           |
| POST   | `/tasks`                    | Create a task                |
| PUT    | `/tasks/{task_id}`          | Update a task                |
| DELETE | `/tasks/{task_id}`          | Delete a task                |
| GET    | `/tasks/{task_id}/comments` | List comments for a task     |
| POST   | `/tasks/{task_id}/comments` | Add a comment to a task      |

## Running the Automated Tests

The `tests/` directory contains a `pytest` suite that exercises the task endpoints (create, get, update, delete, and validation/not-found cases). The tests run directly against a MySQL server (they're not run inside Docker and don't use the `docker compose` setup), so **this section applies whether you're using the Docker or manual setup for the app itself** — either way, you need a MySQL server reachable at `localhost:3306` for the tests.

### 1. Set up a dedicated test database

The tests run against a **separate** MySQL database so they never touch your real data. `tests/conftest.py` creates and drops its own tables automatically on each test run, but the database itself needs to exist first and the connecting user needs privileges on it:

```bash
mysql -u root -p -e "CREATE DATABASE fastapi_test_db;"
mysql -u root -p -e "GRANT ALL PRIVILEGES ON fastapi_test_db.* TO 'task_api'@'localhost';"
```

> The test database name (`fastapi_test_db`) is hardcoded in `tests/conftest.py`. If you rename it there, update the command above to match.

### 2. Set the database password

The tests reuse the same `task_api` MySQL user as the app, and read the password from the same `DB_PASSWORD` environment variable. Make sure it's set in your terminal before running tests:

```bash
export DB_PASSWORD=your_password_here
```

> Unlike `app/db.py`, `tests/conftest.py` connects with a **hardcoded** host of `localhost` on the default MySQL port (`3306`) — it doesn't read `DB_HOST` or use the `docker compose` port mapping (`3307`). So if you're using the `docker compose` database, either temporarily remap it to port `3306` in `docker-compose.yml`, or run a separate local MySQL instance for the tests.

### 3. Run the tests

```bash
pytest
```

For more detail, use `pytest -v`, or run a single file/test with `pytest tests/test_tasks.py` or `pytest tests/test_tasks.py::test_create_task`.

### How the test fixtures work

- The `db_connection` fixture (in `tests/conftest.py`) creates fresh `tasks` and `comments` tables in `fastapi_test_db` before each test, and drops them afterward — so every test starts from a clean, empty database.
- It also monkeypatches `app.db.get_connection` so the app talks to the test database instead of your real `task_tracker` database for the duration of the test.
- The `client` fixture builds on `db_connection` and provides a FastAPI `TestClient` for making requests directly against the app in-process (no running server required).

## Testing the API Manually

### From the browser

With the server running, open the interactive docs:

```
http://127.0.0.1:8000/docs
```

Click any endpoint, then "Try it out," fill in the request body if needed, and "Execute." This works for GET, POST, PUT, and DELETE directly from the page. For simple GET requests you can also just visit the URL directly, e.g. `http://127.0.0.1:8000/tasks`.

### With curl

```bash
# Create a task
curl -X POST http://127.0.0.1:8000/tasks -H "Content-Type: application/json" -d "{\"title\": \"Write tests\", \"completed\": false}"

# List all tasks
curl http://127.0.0.1:8000/tasks

# Get one task
curl http://127.0.0.1:8000/tasks/1

# Update a task
curl -X PUT http://127.0.0.1:8000/tasks/1 -H "Content-Type: application/json" -d "{\"title\": \"Write tests - done\", \"completed\": true}"

# Add a comment
curl -X POST http://127.0.0.1:8000/tasks/1/comments -H "Content-Type: application/json" -d "{\"body\": \"Marked as complete\"}"

# List comments for a task
curl http://127.0.0.1:8000/tasks/1/comments

# Delete a task
curl -X DELETE http://127.0.0.1:8000/tasks/1

# Confirm the task no longer exists (should return 404)
curl -i http://127.0.0.1:8000/tasks/1
```

Add `-i` to any curl command to see the HTTP status code and headers.

## Notes

- `app/db.py` reads `DB_HOST`, `DB_USER`, `DB_NAME`, and `DB_PASSWORD` from environment variables (with local-friendly defaults for everything but the password). `docker-compose.yml` sets all four for the `api` service so it can reach the `db` service by its container name (`db`) instead of `localhost`.
- `tests/conftest.py` does **not** follow the same pattern — it hardcodes `host: "localhost"` and the `fastapi_test_db` database name, and only reads `DB_PASSWORD` from the environment. Keep this in mind if you're testing against the `docker compose` database (see [Running the Automated Tests](#running-the-automated-tests)).
- `owner_id` exists on the `tasks` table but isn't used by any route yet — there's no authentication layer, so tasks aren't currently tied to a specific user.
- The `docker compose` MySQL service maps to host port `3307` (not the default `3306`) to avoid clashing with a MySQL instance you might already have running locally.

## Useful Commands

```bash
# Regenerate schema.sql after changing the database structure
mysqldump -u root -p --no-data task_tracker > schema.sql

# Docker: view logs for a service
docker compose logs -f api

# Docker: get a shell in the running api container
docker compose exec api bash

# Docker: stop and remove containers (add -v to also delete the MySQL data volume)
docker compose down
```