from flask import g, current_app
from sqlalchemy import create_engine, text
from werkzeug.local import LocalProxy

import os

# PostgreSQL database URL
DATABASE_URL = ""
def get_db():
    # Check if a PostgreSQL connection already exists
    db = getattr(g, '_database', None)
    if db is None:
        # Connect to PostgreSQL
        g._database = create_engine(DATABASE_URL)
        db = g._database
    return db

db = LocalProxy(get_db)

def get_data(session_id, start_time, end_time):
    query = """
        SELECT *
        FROM realtime_metrics
        WHERE session_id = :session_id
        AND timestamp BETWEEN :start_time AND :end_time
    """
    with db.connect() as conn:
        result = conn.execute(
            text(query),
            {"session_id": session_id, "start_time": start_time, "end_time": end_time}
        )
        return [dict(row) for row in result]

# Example usage
start_time = "2024-04-23 13:40:29"
end_time = "2024-04-23 13:56:41"
session_id = "your_session_id_here"

data = get_data(session_id, start_time, end_time)
print(data)
