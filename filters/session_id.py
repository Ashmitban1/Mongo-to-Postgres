import dash_mantine_components as dmc 
from dash import dcc, callback, Output, Input, State, html
from sqlalchemy import create_engine, text
from flask import g
from werkzeug.local import LocalProxy

# PostgreSQL database URL
DATABASE_URL = ""

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        g._database = create_engine(DATABASE_URL)
        db = g._database
    return db

db = LocalProxy(get_db)

def SessionIdFilter():
    return dmc.Container(
        children=[
            dmc.Select(
                allowDeselect=False,
                label="Session ID",
                id="session-id-filter",
                style={"marginBottom": "1rem"},
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
    return value

@callback(
    Output("session-id-filter", "data"),
    Input("session-id-offline", "data"),
    Input("url", "href")
)
def update_session_id_values(data, _url):
    try:
        # Retrieve unique session IDs from PostgreSQL
        with db.connect() as conn:
            result = conn.execute(text("SELECT DISTINCT session_id FROM realtime_metrics"))
            session_ids = [row["session_id"] for row in result]
        return sorted(session_ids, key=int)
    except:
        # Return offline session IDs if unable to connect to the PostgreSQL database
        data_string = [str(ids) for ids in data]
        return sorted(data_string, key=int)
