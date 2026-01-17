# CommonTime
A schedule matcher for Cégep students to find common availabilities with their friends.

## Features

- Import your weekly course schedule from Omnivox as a PDF
- Add friends to your group
- Create groups to find common availabilities

> This is a project created for the BrébeufHx 9.0 hackathon.

---

# Installation

```bash
cd schedulematcher
pip install -r requirements.txt
```

## Usage

Database Migrations can be done via:
```bash
python manage.py migrate
```

The development server can be run via:
```bash
python manage.py runserver
```