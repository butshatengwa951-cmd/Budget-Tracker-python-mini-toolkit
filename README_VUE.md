# Productivity Suite — Vue 3

A full-stack evolution of the original Python Budget Tracker / Productivity Suite.

The project started as a Python command-line toolkit and was rebuilt as a web application with a Vue 3 frontend, Flask REST API and PostgreSQL persistence. The original Python work remains in the repository as part of the development history.

## Project Architecture

```
Vue 3 + Vite
      ↓
Flask REST API
      ↓
PostgreSQL
      ↓
Persistent budget, task and study data
```

The application is deployed as separate frontend and backend services on Render, with PostgreSQL used as the production database.

## Stack

- **Vue 3 + Vite** — reactive frontend and component-based UI
- **Python + Flask** — REST API and backend business logic
- **PostgreSQL** — persistent relational database
- **psycopg** — PostgreSQL connection and database access
- **HTML/CSS/JavaScript** — interface structure, styling and client-side behaviour
- **Render** — production frontend and API hosting
- **Neon PostgreSQL** — hosted database used by the deployed application

## Features

### Dashboard

- Current balance, income and expense summaries
- Spending breakdown by category
- Recent transactions
- Open task count
- Planned study time

### Budget Tracking

- Add income and expenses
- Categories and notes
- Persistent transaction storage
- Daily, weekly, monthly and yearly budget cycles
- Automatic period rollover without deleting previous data
- Permanent Budget History
- Archived transaction records for previous periods
- Open an archived period and inspect its income, expenses, balance and transactions
- Delete transactions
- Input validation

### Settings & Budget History

- Choose when the budget resets: daily, weekly, monthly or yearly
- Changing the cycle starts a new current period while preserving previous periods
- Browse historical budget periods
- View detailed information for each archived period
- Existing transactions are assigned to the appropriate budget period during database initialization

### Tasks

- Create tasks
- Low, medium and high priority
- Mark tasks complete
- Delete tasks

### Study Planner

- Create study sessions
- Set a study date
- Record duration in seconds, minutes or hours
- Mark sessions complete
- Track planned study time from the dashboard
- Uses South African local date/time handling

## API

The Flask backend exposes REST endpoints for the application's main workflows, including:

- `/api/health`
- `/api/summary`
- `/api/transactions`
- `/api/budgets`
- `/api/settings`
- `/api/tasks`
- `/api/study`

The health endpoint returns a simple status response and is used to verify the backend is available.

## Running Locally

### Backend

From the project root:

```bash
cd backend

python -m venv venv

# Windows
venv\\Scripts\\activate

# macOS/Linux
# source venv/bin/activate

pip install -r requirements.txt
```

Set a PostgreSQL connection string before starting the API:

```bash
# Windows PowerShell
$env:DATABASE_URL="your-postgresql-connection-string"

# macOS/Linux
export DATABASE_URL="your-postgresql-connection-string"
```

Then run:

```bash
python app.py
```

The API runs locally on:

`http://127.0.0.1:5000`

### Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The Vite development server runs on:

`http://localhost:5173`

During development, Vite proxies `/api` requests to the local Flask server at `http://127.0.0.1:5000`.

For a production-style frontend build:

```bash
npm run build
npm run preview
```

## Environment Variables

### Backend

`DATABASE_URL`  
The PostgreSQL connection string used by Flask and psycopg.

### Frontend

`VITE_API_URL`  
The base URL of the deployed Flask API when the frontend is built for production.

Example:

```text
VITE_API_URL=https://budget-tracker-api-qmgw.onrender.com/api
```

## Deployment

The project is configured as two Render services:

**Frontend**

- Static site
- Root directory: `frontend`
- Build command: `npm install && npm run build`
- Publish directory: `dist`

**Backend**

- Python web service
- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn --bind 0.0.0.0:$PORT app:app`
- Health check: `/api/health`

### Live application

Frontend:

https://budget-tracker-frontend-jf66.onrender.com

API:

https://budget-tracker-api-qmgw.onrender.com

## Development Story

This project is intentionally an evolution rather than a replacement of the original Python exercise.

The first version was a command-line productivity toolkit focused on budgeting, tasks and study planning. The later Vue version transformed those separate tools into a persistent full-stack application with:

- A component-based Vue frontend
- A Flask REST API
- PostgreSQL persistence
- Configurable budget periods
- Historical budget records
- Task and study workflows
- Production deployment through Render

The migration also required working through practical full-stack concerns such as API communication, database integration, production configuration, date handling and maintaining data integrity when budget periods change.

## Colour Palette

- Purple: `#723ECF`
- Pink: `#ED4B86`
- Lavender: `#F4EEF7`
- Warm cream: `#FEF8E7`
