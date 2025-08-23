# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from send_email import send_skill_email
from db_handler import init_db, insert_participant

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
