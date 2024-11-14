from dash import html, dcc, callback
import dash
import dash_mantine_components as dmc
from dash.dependencies import Input, Output
import pandas as pd
from dash_iconify import DashIconify
import plotly.express as px
from sqlalchemy import create_engine

PAGE = "powertrain"
VIZ_ID = "rpm-map-lambda"

# PostgreSQL database connection URL
DATABASE_URL = ""

# Define the start and end timestamps
start_time = "2024-04-23 13:40:29"
end_time = "2024-04-23 13:56:41"

# Query data from PostgreSQL
def get_data():
    engine = create_engine(DATABASE_URL)
    query = f"""
    SELECT * FROM realtime_metrics
    WHERE timestamp >= '{start_time}' AND timestamp <= '{end_time}'
    """
    with engine.connect() as connection:
        df = pd.read_sql(query, connection)
    return df

gc_rpm_map_lambda = dmc.Card(
    children=[
        dmc.CardSection(
            [
                dmc.Group(
                    children=[
                        dmc.Text("RPM vs Map vs Lambda", weight=500),
                        dmc.ActionIcon(
                            DashIconify(icon="carbon:overflow-menu-horizontal"),
                            color="gray",
                            variant="transparent",
                        ),
                    ],
                    position="apart",
                ),
                dmc.Text(
                    children=["This graph shows the RPM vs MAP vs Lambda of the engine over time."],
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

# Callback to generate the graph
@callback(
    Output(f"{PAGE}-{VIZ_ID}", "figure"),
    Input("time-range", "data")
)
def rpm_lambda_graph(_time_range):
    # Fetch data from PostgreSQL within the specified time range
    try:
        df = get_data()
    except Exception as e:
        print("Error loading data:", e)
        return {}

    # Ensure 'timestamp' is in datetime format
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Create scatter plot
    fig = px.scatter(df, x="timestamp", y="MAP", color="Lambda")
    return fig
