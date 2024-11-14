import dash
import pandas as pd
from dash import callback
from dash.dependencies import Input, Output, State
from sqlalchemy import create_engine, text
from flask import g
from werkzeug.local import LocalProxy

# PostgreSQL database URL
DATABASE_URL = ""


# Set up PostgreSQL connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        g._database = create_engine(DATABASE_URL)
        db = g._database
    return db


db = LocalProxy(get_db)


@callback(Output("title", "children"), Input("url", "pathname"))
def update_title(pathname) -> str:
    """Updates the title of the page based on the current pathname."""
    if pathname == "/":
        return "Home"
    else:
        for page in dash.page_registry.values():
            if page["path"] == pathname:
                return page["name"]
    return "404 - Not Found"


@callback(Output("linpot-data", "data"), State("offline-data", "data"), Input("session-id", "data"))
def load_data(_offline_data, session_id):
    if _offline_data is None:
        _offline_data = []

    if session_id is None:
        return []

    try:
        with db.connect() as conn:
            # PostgreSQL query to fetch data for the specified session_id and source "linpot"
            query = """
                SELECT *
                FROM realtime_metrics
                WHERE session_id = :session_id
                AND source = 'linpot'
            """
            result = conn.execute(text(query), {"session_id": session_id})
            data = [dict(row) for row in result]
    except Exception as e:
        # If unable to connect to the database, return offline data
        return _offline_data[int(session_id)] if session_id is not None else []

    # Convert data to a DataFrame
    df = pd.DataFrame(data)

    # Convert DataFrame to JSON and return
    return df.to_json(date_format="iso", orient="split")
