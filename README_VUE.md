# Productivity Suite

A full-stack evolution of my original Python Budget Tracker / Productivity Suite.

## What changed

The original project was a Python command-line toolkit for:
- Budget tracking
- To-do management
- Study planning

The original CLI remains in this repository as part of the project's development history. The upgraded version adds a Vue frontend, Flask REST API and SQLite database.

## Stack

- **Vue 3 + Vite** — interactive frontend
- **Python + Flask** — REST API and backend logic
- **SQLite** — persistent relational storage
- **HTML/CSS/JavaScript** — interface and application behaviour

## Features

### Dashboard
- Balance, income and expense summaries
- Spending by category
- Recent transactions
- Open task count
- Planned study time

### Budget
- Add income and expenses
- Categories and notes
- Transaction history
- Delete transactions
- Input validation

### Tasks
- Create tasks
- Low / medium / high priority
- Mark tasks complete
- Delete tasks

### Study Planner
- Schedule study sessions
- Set duration and date
- Mark sessions complete

## Running locally

### Backend

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate
pip install -r requirements.txt
python app.py
```

The API runs on `http://127.0.0.1:5000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite development server proxies `/api` requests to Flask.

## Development story

This project is intentionally an evolution rather than a replacement of the original Python exercise. It shows the progression from a small command-line application to a structured full-stack system with a component-based frontend, REST API, persistent database and responsive interface.

## Colour palette

- Purple: `#723ECF`
- Pink: `#ED4B86`
- Lavender: `#F4EEF7`
- Warm cream: `#FEF8E7`
