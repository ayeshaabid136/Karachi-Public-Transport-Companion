# Karachi Public Transport Companion

A full-stack web application that helps commuters plan public transport journeys in Karachi. Users can select a starting stop and destination to explore bus journey options, estimated travel times, fares, transfers, and safety information.

Built as a group project for **Software Project Management (506)**, Department of Computer Science, University of Karachi. The project is managed with Scrum, Jira, Microsoft Teams, and Toggl Track.

---

## Features

- Search for stops by name
- Find a journey between any two stops, including bus changes
- Compare three options: **fastest**, **cheapest** and **fewest transfers**
- Distance-based fares (30 PKR for a short ride, up to 200 PKR for a whole route)
- Route details with the ordered list of stops
- Safety advisories for routes and stops
- Automatic tests (20 tests)

**Not included (out of scope):** live GPS tracking, ticketing and payments, native app store deployment.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python | Programming language |
| Django | Web framework |
| Django REST Framework | JSON API |
| PostgreSQL | Database |
| Django Templates | Frontend page rendering |
| HTML5 | Web page structure |
| Bootstrap 5 | Frontend layout and styling |
| CSS3 | Custom styling |
| Django TestCase | Automated tests |

---

## Frontend

The frontend is built using Django templates, HTML, Bootstrap 5, and custom CSS.

- `base.html` provides the shared page layout.
- `home.html` provides the homepage.
- `results.html` displays journey results.
- `style.css` contains custom styling.

The frontend works with the Django project and its existing views and data. Its functionality depends on the implemented backend logic and database.

---

## Bus Routes Included

Five local bus routes, all bidirectional, with 70 different stops.

| Route | Stops | From → To |
|---|---|---|
| Masood Bus | 30 | Malir Halt → Lyari 36 |
| G-17 | 18 | Badar Chowk → University Road |
| F-11 | 18 | Pakhtoonabad → Korangi No. 6 |
| A3 | 13 | Malir Halt → Kemari |
| D7 | 13 | Surjani Town → Tower |

The data is stored in `transport/routes_data.json`. Stop lists come from the team's research. Travel times, bus intervals, service hours, and safety messages are estimates and should be verified.

---

## Project Structure

```text
Karachi-Public-Transport-Companion/
├── config/
│   ├── __init__.py
│   ├── .git.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── planners/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── services.py
│   ├── test_tests.py
│   ├── urls.py
│   └── views.py
├── transport/
│   ├── management/
│   │   └── commands/
│   │       ├── __init__.py
│   │       └── seed_data.py
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── initial.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── routes_data.json
│   ├── serializers.py
│   ├── tests.py
│   └── views.py
├── web/
│   └── static/
│       └── web/
│           ├── images/
│           │   └── Karachi bus.jpg
│           └── style.css
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt
```

---

## Getting Started

### 1. Prerequisites

Install the following before running the project:

- Python 3.10 or newer
- PostgreSQL
- Git

### 2. Clone the Repository

```bash
git clone https://github.com/ayeshaabid136/Karachi-Public-Transport-Companion.git
cd Karachi-Public-Transport-Companion
```

### 3. Create and Activate a Virtual Environment

Create the environment:

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the Database

Create the PostgreSQL database required by the project using pgAdmin or PostgreSQL tools.

Check `config/settings.py` for the database name, username, password configuration, host, and port. Configure these values for your own local PostgreSQL installation.

Do not publish database passwords, Django secret keys, or other credentials in the repository.

### 6. Apply Migrations and Load Data

Create the database tables:

```bash
python manage.py migrate
```

If the project's `seed_data` management command is available, load the project data using:

```bash
python manage.py seed_data
```

To create an administrator account, run:

```bash
python manage.py createsuperuser
```

### 7. Run the Project

```bash
python manage.py runserver
```

Open the local development address in your browser:

`http://127.0.0.1:8000/`

The Django administration page is available at:

`http://127.0.0.1:8000/admin/`

---

## API

The project includes API endpoints for accessing transport information and planning journeys.

All endpoints use `GET` and return JSON. The base path is `/api/`.

| Endpoint | Description |
|---|---|
| `/api/stops/?q=text` | Stops whose name contains the text |
| `/api/routes/` | All routes |
| `/api/routes/<id>/` | One route with its ordered stops and advisories |
| `/api/plan/?from=<id>&to=<id>&mode=<mode>` | Journey options between two stops |
| `/api/safety/?route=<number>` | Safety advisories (all if no route is given) |

The `mode` parameter is optional. Supported modes are `fastest`, `cheapest`, `fewest_transfers`, and `all`.

Stop IDs may change when data is reloaded, so retrieve the current IDs from the stops endpoint before planning a journey.

### Errors

| Situation | Status |
|---|---|
| `from` or `to` is not a number | 400 |
| `from` and `to` are the same stop | 400 |
| Invalid `mode` | 400 |
| Unknown stop ID | 404 |
| No journey exists between the stops | 404 |

---

## How It Works

### Data Model

- **Stop:** A place where a bus stops.
- **Route:** A bus line with its fare range and bus frequency.
- **RouteStop:** The ordered stops of a route, with the minutes from the previous stop.
- **SafetyAdvisory:** A tip or warning for a route or a stop.

Two routes are connected when they share a stop with exactly the same name. Passengers can change buses at shared stops.

### Fare Rule

The fare grows with the number of stops travelled on one bus:

```text
fare = 30 + (200 - 30) × (stops ridden ÷ hops on the route)
```

The result is rounded to the nearest 10. Riding a whole route costs 200 PKR. When a journey needs two buses, the fares are added.

### Route Search

The stops and rides are treated as a graph, and the search uses **Dijkstra's algorithm**. The search considers both the current stop and the bus being used.

- **Ride:** Travel to the next or previous stop on the same bus. The cost is the travel time between stops.
- **Board or transfer:** Board a bus or change buses at the current stop. The cost is the estimated waiting time, based on half the bus interval.

The three modes use the same algorithm with different costs:

| Mode | Extra cost when boarding | Extra cost per stop ridden |
|---|---|---|
| `fastest` | None | None |
| `cheapest` | Minimum fare × 1000 | Stop fare × 1000 |
| `fewest_transfers` | 1000 | None |

The large multiplier makes fare or the number of buses the main priority in the relevant modes, while travel time helps break ties. The route-search logic is implemented in `planner/services.py`.

### Assumptions

- Routes run in both directions with the same travel times.
- Estimates come from scheduled data, not live tracking.
- Each stop appears only once on a route.

---

## Testing

The existing project README reports 20 automated tests. These tests cover journey-planning modes, reverse trips, fare calculations, safety advisories, API endpoints, error responses, and loading the transport data.

Run the test suite with:

```bash
python manage.py test
```

---

## Troubleshooting

| Problem | Possible solution |
|---|---|
| Database does not exist | Create the database configured in `config/settings.py`. |
| `psycopg2-binary` is not found | Install dependencies using `pip install -r requirements.txt`. |
| Django commands are not recognised | Activate the virtual environment and run commands using `python manage.py`. |
| API returns an invalid stop ID error | Use valid stop IDs retrieved from `/api/stops/`. |
| Database tables are missing | Run `python manage.py migrate`. |

---

## Limitations and Future Work

- No live bus tracking.
- Only five routes are included; travel times, intervals, and safety messages need verification.
- The fastest mode can suggest several bus changes because waiting time is counted at every boarding.
- Stop coordinates are not filled in yet, so a map view is not possible until they are added.

---

## Team

Software Project Management (506), 6th semester, University of Karachi.

| Name | Role |
|---|---|
| Nida Hafeez | Team Lead |
| Mahnoor Khan & Romaisa Ejaz | Backend development |
| Ayesha Abid && Ayesha Khan | Frontend / UI-UX |
| Nida Hafeez and Mahnoor Khan | Data research |
