# Aab-e-Panah

A flood relief and evacuation coordination system for a university DSA term project.
It helps organize flood relief resources, evacuation plans, and coordination work.

## Three layers

- Web UI: HTML, CSS, and JavaScript
- Backend: Python, OOP, and Flask
- Database: MySQL

## First time setup

1. Create and activate the virtual environment:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

2. Install the requirements:

```powershell
python -m pip install -r requirements.txt
```

3. Create the MySQL database and user:

```sql
CREATE DATABASE aab_e_panah;
CREATE USER 'aab_user'@'localhost' IDENTIFIED BY 'choose_a_password';
GRANT ALL PRIVILEGES ON aab_e_panah.* TO 'aab_user'@'localhost';
FLUSH PRIVILEGES;
```

4. Copy `.env.example` to `.env` and put the password in it. Never commit
`.env`.

5. Run `backend/database/setup_db.py` twice in a row. It asks for `YES`
because it clears the sample tables. Both runs should finish successfully.

6. Run the tests and start the app using the commands below.

## Features so far

- Camp and aid request management
- Merge sort and counting sort are stable. Quick sort is not stable.
- Camp supply batches with soonest-expiry issuing
- In-memory undo for added camps and supplies
- Camp arrivals and departures with capacity checks
- Audit log filtering and viewing
- Audit log removes line breaks
- Tests use their own audit log files

## How to run

Activate the virtual environment, then run these commands from the project root:

```powershell
venv\Scripts\python.exe tests\test_structures.py
venv\Scripts\python.exe tests\test_algorithms.py
venv\Scripts\python.exe tests\test_api_validation.py
venv\Scripts\python.exe tests\test_requests_db.py
venv\Scripts\python.exe tests\test_supplies.py
venv\Scripts\python.exe tests\test_occupancy.py
venv\Scripts\python.exe tests\test_audit_viewer.py
venv\Scripts\python.exe scripts\sort_benchmark.py
venv\Scripts\flask.exe --app backend.app run --debug
```

The database test needs the MySQL settings in `.env` and the schema from
`backend/database/schema.sql`.

Open the displayed Flask address in a browser. Use the camps controls to sort
by name, capacity, or free space with merge sort or quick sort. Use either
camp search form to find a camp. The aid requests page shows arrival order,
ranked severity order, and the serve button. Ranking does not change serving
order. Use the Camp Supplies section to add and issue batches, and use the
Undo section to undo the newest camp or supply addition.
