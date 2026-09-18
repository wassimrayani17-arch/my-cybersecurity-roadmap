# Task Tracker API

A lightweight RESTful API built with Python, FastAPI, and MySQL for managing tasks and comments.

## Features

- CRUD operations for tasks (create, list, get, update, delete)
- Comments attached to individual tasks
- Request/response validation via Pydantic
- Interactive OpenAPI docs at `/docs` out of the box
- Automated `pytest` test suite covering the task endpoints

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
├── schema.sql        # Database schema (users, tasks, comments)
└── requirements.txt
```

## Requirements

- Python 3.11+
- MySQL 8.0+

## Setup

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

### 5. Set the database password

`app/db.py` connects with a fixed host, user, and database name (`localhost`, `task_api`, `task_tracker`), but reads the **password** from an environment variable rather than storing it in the code:

```python
password=os.environ["DB_PASSWORD"],
```

Before starting the server, set it in your terminal:

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

This only lasts for the current terminal session — you'll need to set it again each time you open a new terminal to run the server.

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

The `tests/` directory contains a `pytest` suite that exercises the task endpoints (create, get, update, delete, and validation/not-found cases).

### 1. Set up a dedicated test database

The tests run against a **separate** MySQL database so they never touch your real data. `tests/conftest.py` creates and drops its own tables automatically on each test run, but the database itself needs to exist first and the connecting user needs privileges on it:

```bash
mysql -u root -p -e "CREATE DATABASE fastapi_test_db;"
mysql -u root -p -e "GRANT ALL PRIVILEGES ON fastapi_test_db.* TO 'task_api'@'localhost';"
```

> The test database name (`fastapi_test_db`) is hardcoded in `tests/conftest.py`. If you rename it there, update the command above to match.

### 2. Set the database password

The tests reuse the same `task_api` MySQL user as the app, and read the password from the same `DB_PASSWORD` environment variable described in [step 5 of Setup](#5-set-the-database-password). Make sure it's set in your terminal before running tests:

```bash
export DB_PASSWORD=your_password_here
```

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

- `DB_HOST`, `DB_USER`, and `DB_NAME` are currently hardcoded in `app/db.py` (`localhost`, `task_api`, `task_tracker`). This is fine for local development; if this project is deployed elsewhere, those should move to environment variables too, since the host and database name are likely to differ per environment.
- `owner_id` exists on the `tasks` table but isn't used by any route yet — there's no authentication layer, so tasks aren't currently tied to a specific user.

commands:
if you made a new schema:   mysqldump -u root -p --no-data task_tracker > schema.sql