# [Insert project name here]
A schedule matcher for Cégep students suffering under the  administration of the infamous Omnivox application.

This app allows users to import their weekly course schedule, add friends, and create groups in order to find common availabilities.

Please watch the instructional video below showing how to export your course schedule as a PDF.

[youtube url]

This is a project created for the BrébeufHx 9.0 hackathon.

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