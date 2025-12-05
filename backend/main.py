from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
import sqlite3
import requests
import os

app = FastAPI()

# Allow CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class Ticket(BaseModel):
    user_id: str  # Changed to str to accept emails or UUIDs from frontend
    problem_description: str
    priority: str # e.g., "Low", "Medium", "High"
    category: str # e.g., "Technical", "Billing", "Access"

class TicketResponse(BaseModel):
    ticket_id: int
    status: str
    message: str
    queue: str

class MetricsResponse(BaseModel):
    total_tickets: int
    closed_tickets: int
    tickets_by_classification: Dict[str, int]
    tickets_by_queue: Dict[str, int]

# --- Database Setup ---
DB_NAME = "tickets.db"

def init_db():
    # Connect to the database inside the backend folder
    db_path = os.path.join(os.path.dirname(__file__), DB_NAME)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Added 'queue' column for routing logic
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            problem_description TEXT NOT NULL,
            priority TEXT NOT NULL,
            category TEXT NOT NULL,
            status TEXT NOT NULL,
            ml_classification TEXT,
            queue TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db() # Initialize the database on startup

# --- ML Service Integration ---
# Use environment variable for flexibility (Docker support)
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8001")

def classify_ticket_with_ml(ticket: Ticket):
    """Calls the ML service to classify the ticket."""
    try:
        response = requests.post(f"{ML_SERVICE_URL}/predict", json=ticket.dict())
        response.raise_for_status()
        return response.json().get("problem_type", "Unknown")
    except requests.exceptions.RequestException as e:
        print(f"Error calling ML service: {e}")
        return "Manual Review Needed" 

def get_auto_reply_from_ml(problem_type: str):
    """Gets a templated response from the ML service."""
    try:
        response = requests.post(f"{ML_SERVICE_URL}/auto_reply", json={"problem_type": problem_type})
        response.raise_for_status()
        return response.json().get("reply", "We have received your ticket and will process it shortly.")
    except requests.exceptions.RequestException as e:
        print(f"Error calling ML service for auto-reply: {e}")
        return "We have received your ticket and will process it shortly."


# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Helpdesk Core API is running. Go to /docs for documentation."}

@app.post("/submit_ticket", response_model=TicketResponse)
def submit_ticket(ticket: Ticket):
    """
    Receives a new ticket, classifies it, and decides on the routing logic.
    """
    db_path = os.path.join(os.path.dirname(__file__), DB_NAME)
    
    # 1. Classify with ML Service (Task 2)
    ml_classification = classify_ticket_with_ml(ticket)

    # 2. Routing Logic (Task 3 implementation)
    # Checking Problem Type, Priority, and Category
    status = "Pending"
    message = "Ticket submitted successfully."
    queue = "General"

    # A. Check Problem Type (ML)
    if ml_classification == "Типовой инцидент": 
        # Task 5: Automated Solution
        status = "Closed"
        queue = "Automated"
        message = get_auto_reply_from_ml(ml_classification)
    
    else:
        # B. Check Priority and Category for routing
        if ticket.priority.lower() == "high" or ticket.priority.lower() == "critical":
            queue = "HighPriority"
            message = "Ticket escalated to High Priority team."
        elif ticket.category.lower() == "billing":
            queue = "Billing"
        elif ticket.category.lower() == "technical":
            queue = "TechSupport"
        else:
            queue = "GeneralSupport"

    # 3. Save to Database (Task 4)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tickets (user_id, problem_description, priority, category, status, ml_classification, queue) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (ticket.user_id, ticket.problem_description, ticket.priority, ticket.category, status, ml_classification, queue)
    )
    ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return TicketResponse(ticket_id=ticket_id, status=status, message=message, queue=queue)

@app.get("/metrics", response_model=MetricsResponse)
def get_metrics():
    """Provides simple metrics about the tickets for dashboard (Task 4)."""
    db_path = os.path.join(os.path.dirname(__file__), DB_NAME)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        total_tickets = cursor.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
        closed_tickets = cursor.execute("SELECT COUNT(*) FROM tickets WHERE status = 'Closed'").fetchone()[0]
        
        classifications = cursor.execute("SELECT ml_classification, COUNT(*) as count FROM tickets GROUP BY ml_classification").fetchall()
        queues = cursor.execute("SELECT queue, COUNT(*) as count FROM tickets GROUP BY queue").fetchall()
    except sqlite3.OperationalError:
         # Return zero values if DB is empty or not init
         return {
            "total_tickets": 0,
            "closed_tickets": 0,
            "tickets_by_classification": {},
            "tickets_by_queue": {}
         }
    finally:
        conn.close()

    return {
        "total_tickets": total_tickets,
        "closed_tickets": closed_tickets,
        "tickets_by_classification": {row['ml_classification']: row['count'] for row in classifications},
        "tickets_by_queue": {row['queue']: row['count'] for row in queues}
    }
