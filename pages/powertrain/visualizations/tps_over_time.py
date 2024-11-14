from dash import callback, dcc, html
import dash
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
from dash_iconify import DashIconify
from sqlalchemy import create_engine

PAGE = "powertrain"
VIZ_ID = "tps-over-time"

# PostgreSQL connection URL
DATABASE_URL = ""

# Define the start and end timestamps
start_time = "2024-04-23 13:40:29"
end_time = "2024-04-23 13:56:41"

# Query data from PostgreSQL
def get_linpot_data():
    engine = create_engine(DATABASE_URL)
    query = f"""
    SELECT timestamp, "Front Left", "Front Right", "Rear Left", "Rear Right" 
    FROM realtime_metrics
    WHERE timestamp >= '{start_time}' AND timestamp <= '{end_time}'
    """
    with engine.connect() as connection:
        df = pd.read_sql(query, connection)
    return df

gc_tps_over_time = dmc.Card(
    id="tps-over-time",
    children=[
        dmc.CardSection(
            [
                dmc.Group(
                    children=[
                        dmc.Text("Linpots vs Time", weight=500),
                        dmc.ActionIcon(
                            DashIconify(icon="carbon:overflow-menu-horizontal"),
                            color="gray",
                            variant="transparent",
                        ),
                    ],
                    position="apart",
                ),
                dmc.Text(
                    children=[
                        "Data from the latest testing session"
                    ],
                    mt="sm",
                    color="dimmed",
                    size="sm",
                ),
            ],
            inheritPadding=True,
            py="xs",
            withBorder=True,
        ),
        dmc.CardSection(
            dcc.Loading(
                dcc.Graph(id=f"{PAGE}-{VIZ_ID}"),
            ),
        ),
    ],
    withBorder=True,
    shadow="sm",
    radius="md",
    p="xs",
    m="xs",
    bg="black",
    style={"width": "100%"},
)

# Callback to generate the Linpots over time graph
@callback(
    Output(f"{PAGE}-{VIZ_ID}", "figure"),
    Input("linpot-data", "data")
)
def tps_over_time_graph(_data):
    # Fetch data from PostgreSQL within the specified time range
    try:
        df = get_linpot_data()
    except Exception as e:
        print("Error loading data:", e)
        return px.line(title="No Data", labels={"value": "TPS", "timestamp": "Time"})

    # Ensure 'timestamp' is in datetime format
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Create line plot for Linpots data
    fig = px.line(
        df,
        x="timestamp",
        y=["Front Left", "Front Right", "Rear Left", "Rear Right"],
        labels={"value": "TPS", "timestamp": "Time"}
    )
    return fig
