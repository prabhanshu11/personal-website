from fastlite import *
from dataclasses import dataclass
from datetime import datetime
import os

# Ensure data directory exists
# We use an absolute path relative to the app root if possible, 
# but relying on CWD being the project root is standard for this setup.
os.makedirs('data', exist_ok=True)

# Connect to database
db = database('data/site.db')

@dataclass
class Subscriber:
    id: int
    email: str
    created_at: str
    status: str

# Create table if not exists
subscribers = db.t.subscribers
if "subscribers" not in db.t:
    subscribers.create({
        "id": int,
        "email": str,
        "created_at": str,
        "status": str,
    }, pk="id")

def add_subscriber(email: str) -> tuple[int, bool]:
    """
    Adds a subscriber.
    Returns (user_id, created) tuple.
    created is True if new, False if already existed.
    """
    # Check if already exists
    # FastLite's tables are callable for queries
    # Note: Avoid raw SQL injection by using parameter binding if possible, 
    # but fastlite often handles basic wrapper stuff. 
    # For safety with simple strings in fastlite/sqlite-minutils:
    results = subscribers(where='email = ?', where_args=[email])
    
    if results:
        return results[0]['id'], False
        
    # Add new subscriber
    # id is auto-incrementing integer as strictly defined by sqlite-minutils when int pk is used?
    # Actually fastlite handles 'id' specially if passed as None or omitted if dataclass field allows it.
    # We pass explicit dict or object.
    
    new_sub = Subscriber(
        id=None, 
        email=email,
        created_at=datetime.utcnow().isoformat(),
        status='active'
    )
    
    # insert returns the inserted object including the new ID
    res = subscribers.insert(new_sub)
    return res['id'], True

def get_count():
    return len(subscribers())

def get_all_subscribers():
    """
    Returns all subscribers ordered by created_at desc.
    """
    return subscribers(order_by='created_at DESC')

def delete_subscriber(id: int):
    """
    Deletes a subscriber by ID.
    """
    subscribers.delete(id)
