# Aab-e-Panah

A flood relief and evacuation coordination system for a university DSA term project.
It helps organize flood relief resources, evacuation plans, and coordination work.

## Three layers

- Web UI: HTML, CSS, and JavaScript
- Backend: Python, OOP, and Flask
- Database: MySQL

## How to run

Activate the virtual environment, then run these commands from the project root:

```powershell
venv\Scripts\python.exe tests\test_structures.py
venv\Scripts\python.exe tests\test_algorithms.py
venv\Scripts\python.exe tests\test_api_validation.py
venv\Scripts\python.exe tests\test_requests_db.py
venv\Scripts\python.exe scripts\sort_benchmark.py
venv\Scripts\flask.exe --app backend.app run --debug
```

The database test needs the MySQL settings in `.env` and the schema from
`backend/database/schema.sql`.

Open the displayed Flask address in a browser. Use the camps controls to sort
by name, capacity, or free space with merge sort or quick sort. Use either
camp search form to find a camp. The aid requests page shows arrival order,
ranked severity order, and the serve button. Ranking does not change serving
order.
