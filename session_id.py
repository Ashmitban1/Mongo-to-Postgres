import dash_mantine_components as dmc
from dash import dcc, callback, Output, Input, State, html
from flask import g
import psycopg2
import os

# PostgreSQL database URL
DB_URL = 'postgresql://postgres:feCDeC3CE6e2eCfD43bg11625f1Cg233@autorack.proxy.rlwy.net:30549/railway'

# PostgreSQL connection setup
def get_db():
    """Establish and return a PostgreSQL database connection."""
    db = getattr(g, '_database', None)
    if db is None:
        try:
            db = g._database = psycopg2.connect(DB_URL)
        except psycopg2.OperationalError as e:
            print(f"Error connecting to PostgreSQL: {e}")
            return None
    return db

def close_db(e=None):
    """Close the PostgreSQL database connection."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def SessionIdFilter():
    """Creates a container for session ID selection."""
    return dmc.Container(
        children=[
            dmc.Select(
                allowDeselect=False,
                label="Session ID",
                id="session-id-filter",
                sx={"marginBottom": "1rem"},
                data=[]
            ),
            dcc.Store(id="session-id", storage_type="session", data=0)
        ]
    )

@callback(
    Output("session-id", "data"),
    Input("session-id-filter", "value")
)
def update_session_id(value):
    """Updates the session ID stored in the session."""
    return value

@callback(
    Output("session-id-filter", "data"),
    Input("session-id-offline", "data"),
    Input("url", "href")
)
def update_session_id_values(data, _url):
    """Fetches distinct session IDs from PostgreSQL or falls back to offline data."""
    db = get_db()
    if db is None:
        # Returns offline session IDs if unable to connect to PostgreSQL
        data_string = [str(ids) for ids in data]
        return sorted(data_string)

    try:
        cursor = db.cursor()

        # PostgreSQL query to get distinct session IDs from JSON metadata
        query = "SELECT DISTINCT metadata->>'session_id' AS session_id FROM realtime_metrics;"
        cursor.execute(query)
        session_ids = [row[0] for row in cursor.fetchall()]

        cursor.close()

        # Filter out non-numeric session IDs
        session_ids = [sid for sid in session_ids if sid.isdigit()]
        return sorted(session_ids, key=int)
    except Exception as e:
        print(f"Error fetching session IDs from PostgreSQL: {e}")
        # Fallback to offline data in case of error
        data_string = [str(ids) for ids in data]
        return sorted(data_string)
