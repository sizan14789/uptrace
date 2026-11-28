# Uptrace

A backend uptime monitoring system built with **Python, FastAPI, PostgreSQL, and HTTPX**. It periodically checks registered websites, determines whether they are UP or DOWN, and stores monitoring results for historical tracking.

## Features

- **Website Monitoring** — Checks the availability of registered websites through HTTP requests.
- **Configurable Intervals** — Each monitor has its own checking interval.
- **Timeout Handling** — Uses configurable request timeouts to prevent checks from waiting indefinitely.
- **Status Tracking** — Classifies websites as UP or DOWN based on their HTTP response status.
- **Error Handling** — Captures connection errors, timeouts, and other request exceptions.
- **Result Persistence** — Stores monitoring results, including status codes and errors, in PostgreSQL.
- **Monitoring History** — Retrieves historical monitoring results for individual websites.
- **REST API** — Provides endpoints to access monitor information and monitoring statuses.
- **Manual Checking** — Allows checking all active websites manually without saving the results.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastAPI | REST API framework |
| PostgreSQL | Database |
| asyncpg | Asynchronous PostgreSQL connection pool |
| HTTPX | Asynchronous HTTP requests |
| Pydantic Settings | Environment-based configuration |
| asyncio | Asynchronous scheduling and task management |

## Project Structure

```text
uptime-monitor/
│
├── app/
│   ├── __init__.py
│   ├── app.py
│   ├── checker.py
│   ├── config.py
│   ├── db.py
│   └── scheduler.py
│
├── .env
├── .gitignore
└── requirements.txt
```

## How It Works

The application consists of four main components.

### 1. Database Connection (`db.py`)

Uses `asyncpg` to establish an asynchronous connection pool with PostgreSQL.

- Creates a connection pool when the application starts.
- Allows API endpoints and the scheduler to execute database queries.
- Closes the connection pool when the application shuts down.

The connection pool is configured with a maximum of 10 connections.

### 2. Website Checker (`checker.py`)

Responsible for checking whether a website is accessible.

It uses `httpx.AsyncClient` to send HTTP GET requests to the target URL.

For each request, it:

1. Sends an HTTP GET request with the configured timeout.
2. Retrieves the HTTP response status code.
3. Classifies the website as:
   - **UP** — HTTP status code is below 400.
   - **DOWN** — HTTP status code is 400 or above.
4. Captures request exceptions and returns the error information.

The checker returns a dictionary containing:

- `up` — Whether the website is considered available.
- `status_code` — HTTP response status code, if available.
- `error` — Error message, if an exception occurs.

The HTTP client is automatically closed after each check.

### 3. Monitoring Scheduler (`scheduler.py`)

Responsible for automatically checking active websites at their configured intervals.

The scheduler consists of two asynchronous functions:

**`tick()`**

- Retrieves all monitors with ACTIVE status.
- Checks whether each monitor is due for another check.
- Skips monitors that have not reached their configured interval.
- Calls the website checker for monitors that are due.
- Saves each result in the `monitoring_results` table.

A dictionary named `last_checked_at` tracks the last check time of each monitor in memory.

**`engine()`**

Runs the monitoring cycle continuously:

1. Executes `tick()`.
2. Waits 60 seconds.
3. Repeats the process.

Each monitor's individual interval determines when it is actually checked, rather than checking every website on every scheduler cycle.

### 4. REST API (`app.py`)

FastAPI provides endpoints to retrieve monitoring information and perform manual checks.

The database connection is managed through FastAPI's lifespan context manager.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Checks whether the API is running. |
| GET | `/monitors` | Retrieves all registered monitors. |
| GET | `/monitors/{monitor_id}` | Retrieves information about a specific monitor. |
| GET | `/status` | Retrieves the latest monitoring result for each monitor. |
| GET | `/status/{monitor_id}` | Retrieves the monitoring history of a specific monitor. |
| GET | `/check` | Manually checks all active monitors without saving results. |

### Endpoint Details

**GET `/health`**

Returns the application health status.

**GET `/monitors`**

Returns all registered monitors from the database.

**GET `/monitors/{monitor_id}`**

Returns information about a specific monitor. Returns HTTP 404 if the monitor does not exist.

**GET `/status`**

Uses PostgreSQL's `DISTINCT ON` to retrieve the latest monitoring result for each monitor, ordered by check time.

**GET `/status/{monitor_id}`**

Returns the historical monitoring results of a specific monitor, ordered from newest to oldest.

**GET `/check`**

Performs an immediate check of all active monitors and returns their current availability without inserting anything into the monitoring results table.

## Configuration

The application uses Pydantic Settings to load environment variables from a `.env` file.

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/uptime_monitor
```

Replace the credentials and database name with your PostgreSQL configuration.

## Installation and Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd uptime-monitor
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows:**

```bash
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create the `.env` file and provide your PostgreSQL connection URL.

### 5. Start the application

```bash
uvicorn app.app:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

### 6. Explore the API

FastAPI provides interactive API documentation through Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Current Implementation Notes

- The automatic scheduler is implemented but currently disabled in the FastAPI lifespan function.
- Monitoring intervals and last-check timestamps are maintained in memory by the scheduler.
- The scheduler currently processes monitors sequentially.
- The manual checking endpoint does not persist results.
- Monitor registration and management endpoints are not implemented yet.

