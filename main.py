# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
import os
import re
from pydantic import BaseModel
from send_email import send_skill_email, build_pdf_lookup, normalize
from db_handler import init_db, insert_participant
from datetime import datetime

#LOG_DIR = Path("D:/aiprojects/logs") 
LOG_FILE = Path("/home/kumaresh/logs/course_access.log")  # Use your Linux path if needed

#LOG_FILE = Path("D:/aiprojects/logs/course_access.log")  # file will be created in backend folder

app = FastAPI()

# Initialize DB when app starts
init_db()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    #allow_origins=["http://localhost:5173"],  # Adjust if deploying
    allow_origins=["http://4.240.101.142"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Learner(BaseModel):
    name: str
    email: str
    contact: str
    experience: str
    current_skill: str
    wish_to_upskill: list[str]

def log_course_access(course_name: str, status: str):
    timestamp = datetime.now().strftime("%d-%m-%Y- %H:%M:%S")
    log_entry = f"{timestamp} | {course_name} | {status}\n"
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)


@app.post("/submit")
async def submit_form(data: Learner):
    #print("--------------------------- Inside submit_form" + data.name+data.email+data.contact+data.wish_to_upskill+ data.current_skill + data.experience)

    try:
        # Insert participant into SQLite
        insert_participant(
            name=data.name,
            email=data.email,
            contact=data.contact,
            experience=data.experience,  # Using experience as placeholder
            current_skill=data.current_skill,
            wish_to_upskill=data.wish_to_upskill
        )

        # Send email
        send_skill_email(data.name, data.email, data.wish_to_upskill)
        return {
            "status": "success",
            "message": f"Thank you {data.name}! Please check your email for the learning resource."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Email could not be sent. Error: {str(e)}"
        }


# ------------------------------
# Catalogue PDF Serving
# ------------------------------
#RESOURCE_DIR = Path("D:/aiprojects/resources")  # Same as send_email.py
RESOURCE_DIR = Path("/home/kumaresh/resources")  # Use your Linux path if needed



# Build lookup for PDFs (key=normalized course name, value=filename)
pdf_lookup = build_pdf_lookup(RESOURCE_DIR)

@app.get("/course-pdf")
def get_course_pdf(course: str):
    course_key = normalize(course)
    filename = pdf_lookup.get(course_key)
    if not filename:
        raise HTTPException(status_code=404, detail="Course PDF not found")
    
    file_path = RESOURCE_DIR / filename
    if not file_path.exists():
        log_course_access(course, "File missing")
        raise HTTPException(status_code=404, detail="PDF file missing on server")

      #  Log the access to the course
    log_course_access(course, "success")
    
    return FileResponse(file_path, media_type="application/pdf")