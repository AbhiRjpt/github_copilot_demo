"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
import threading
import re

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    }
}
# Simple global lock to reduce race conditions on signups
_signup_lock = threading.Lock()
# Basic email regex for minimal validation
_email_re = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup", status_code=201)
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Basic email validation
    if not email or not _email_re.match(email.strip()):
        raise HTTPException(status_code=400, detail="Invalid email address")

    email = email.strip().lower()

    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Perform checks and update under lock to reduce race conditions
    with _signup_lock:
        # Check if already signed up
        if email in (p.lower() for p in activity.get("participants", [])):
            raise HTTPException(status_code=400, detail="Email already signed up for this activity")

        # Check capacity
        max_participants = activity.get("max_participants")
        participants = activity.get("participants", [])
        if isinstance(max_participants, int) and len(participants) >= max_participants:
            raise HTTPException(status_code=400, detail="Activity is full")

        # Add student
        participants.append(email)

    return {"message": f"Signed up {email} for {activity_name}"}
