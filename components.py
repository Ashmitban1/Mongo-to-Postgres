from dash import callback
import dash
import pandas as pd
from flask import g
from dash.dependencies import Input, Output, State
import psycopg2
import os

# PostgreSQL database URL (update if necessary)
DB_URL = 'postgresql://postgres:feCDeC3CE6e2eCfD43bg11625f1Cg233@autorack.proxy.rlwy.net:30549/railway'

def get_db():
    """Establish and return a PostgreSQL database connection."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = psycopg2.connect(DB_URL)
    return db

def close_db(e=None):
    """Close the PostgreSQL database connection."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@callback(Output("title", "children"), Input("url", "pathname"))
def update_title(pathname) -> str:
    """Updates the title of the page based on the current pathname.

    Args:
        pathname (str): The current pathname of the page.

    Returns:
        str: The title of the page.
    """
    if pathname == "/":
        return "Home"
    else:
        for page in dash.page_registry.values():
            if page["path"] == pathname:
                return page["name"]
    return "404 - Not Found"

@callback(Output("linpot-data", "data"), State('offline-data', 'data'), Input("session-id", "data"))
def load_data(_offline_data, session_id):
    """Loads data for the given session ID from PostgreSQL or offline data if unavailable.

    Args:
        _offline_data (list): The offline data.
        session_id (str): The current session ID.

    Returns:
        str: JSON data of the queried metrics.
    """
    if _offline_data is None:
        _offline_data = []

    # If session ID is None, return empty list
    if session_id is None:
        return []

    start_time = "2024-04-23 13:40:29"
    end_time = "2024-04-23 13:56:41"

    try:
        db = get_db()
        cursor = db.cursor()

        # PostgreSQL query to fetch data based on session_id, source "linpot", and timestamp range
        query = """
        SELECT * 
        FROM realtime_metrics
        WHERE metadata->>'session_id' = %s
          AND metadata->>'source' = 'linpot'
          AND timestamp BETWEEN %s AND %s;
        """
        cursor.execute(query, (str(session_id), start_time, end_time))
        records = cursor.fetchall()

        # Fetch column names from the cursor description
        columns = [desc[0] for desc in cursor.description]

        # Convert the query results to a DataFrame
        df = pd.DataFrame(records, columns=columns)
        cursor.close()

        # Convert DataFrame to JSON and return
        return df.to_json(date_format="iso", orient="split")

    except Exception as e:
        print(f"Error fetching data from PostgreSQL: {e}")
        # Fallback to offline data if unable to connect to PostgreSQL
        return _offline_data[int(session_id)] if session_id != None else []
    finally:
        close_db()
