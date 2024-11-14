import dash_mantine_components as dmc
from dash import dcc, callback, Output, Input, State, html
from flask import g
import pandas as pd
import psycopg2
import os

# PostgreSQL database URL
DB_URL = ''

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
    finally:
        close_db()

@callback(
    Output("metrics-output", "children"),
    Input("session-id", "data")
)
def fetch_metrics_data(session_id):
    """Fetches metrics data within the specified time range for the selected session ID."""
    if session_id is None:
        return "Please select a Session ID."

    # Define the time range
    start_time = "2024-04-23 13:40:29"
    end_time = "2024-04-23 13:56:41"

    db = get_db()
    if db is None:
        return "Failed to connect to the database."

    try:
        cursor = db.cursor()

        # Query to fetch all metrics within the specified time range for the selected session ID
        query = """
        SELECT * 
        FROM realtime_metrics
        WHERE metadata->>'session_id' = %s
          AND timestamp BETWEEN %s AND %s;
        """
        cursor.execute(query, (session_id, start_time, end_time))
        records = cursor.fetchall()

        # If no data is found, display a message
        if not records:
            return "No data found for the selected session ID and time range."

        # Fetch column names from the cursor description
        columns = [desc[0] for desc in cursor.description]

        # Convert the query results to a DataFrame
        df = pd.DataFrame(records, columns=columns)

        # Generate a table or other output from the DataFrame
        return dmc.Table(
            children=[
                html.Thead(html.Tr([html.Th(col) for col in columns])),
                html.Tbody([
                    html.Tr([html.Td(df.iloc[i][col]) for col in columns])
                    for i in range(len(df))
                ])
            ]
        )
    except Exception as e:
        print(f"Error fetching metrics data from PostgreSQL: {e}")
        return "Error fetching data from PostgreSQL."
    finally:
        cursor.close()
        close_db()
