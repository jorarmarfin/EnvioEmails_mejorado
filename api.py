from fastapi import FastAPI
import os
import json

app = FastAPI(
    title="Email Campaign API",
    description="API to query campaign information and submissions.",
    version="1.1.0"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COUNTER_FILE = os.path.join(BASE_DIR, 'contador', 'contador.txt')
CAMPAIGNS_HISTORY_FILE = os.path.join(BASE_DIR, 'campaigns.json')

def read_total_sent_counter() -> int:
    """Reads the current number from the global submission counter."""
    try:
        with open(COUNTER_FILE, 'r') as f:
            content = f.read().strip()
            return int(content) if content else 0
    except (FileNotFoundError, ValueError):
        return 0

def read_campaigns_history() -> list:
    """Reads the campaign history from the JSON file."""
    try:
        with open(CAMPAIGNS_HISTORY_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

@app.get("/api/campaigns", tags=["Campaigns"])
def get_campaigns_history():
    """
    Gets the list of historical campaigns from the campaigns.json file.
    This data is maintained manually.
    """
    return read_campaigns_history()

@app.get("/api/sent/total", tags=["Counter"])
def get_total_sent():
    """
    Gets the total number of emails sent by the application (global counter).
    """
    total_sent = read_total_sent_counter()
    return {"total_emails_sent": total_sent}