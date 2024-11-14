from dash import html, dcc, callback
import dash
import dash_mantine_components as dmc
from dash.dependencies import Input, Output
import pandas as pd
from dash_iconify import DashIconify
import plotly.express as px
from sqlalchemy import create_engine

PAGE = "powertrain"
VIZ_ID = "customizable_graph"
ID = f"{PAGE}-{VIZ_ID}"

# Define the PostgreSQL connection URL
DATABASE_URL = ""

# Set the start and end times
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

# Load data from PostgreSQL
try:
    df = get_data()
except Exception as e:
    print("Error loading data:", e)
    df = pd.DataFrame()  # Fallback to an empty DataFrame if query fails

# Ensure 'timestamp' is in datetime format
if not df.empty and 'timestamp' in df.columns:
    df['timestamp'] = pd.to_datetime(df['timestamp'])

# Prepare options for y-axis dropdown based on column names
y_axis_options = [{'label': col, 'value': col} for col in df.columns if col not in ["timestamp", "brand", "model", "year"]]

# Define the Dash component
gc_customizable_graph = dmc.Card(
    id="customizable-ecu-data",
    children=[
        dmc.CardSection(
            [
                dmc.Group(
                    children=[
                        dmc.Text("RPM vs Map vs Lambda", weight=500, id="graph-title"),
                        dmc.ActionIcon(
                            DashIconify(icon="carbon:overflow-menu-horizontal"),
                            color="gray",
                            variant="transparent",
                        ),
                    ],
                    position="apart",
                ),
                dmc.Text(
                    children=["This graph can be configured for any value of the engine over time."],
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
            [
                dmc.MultiSelect(
                    id="y-axis-dropdown",
                    data=y_axis_options,
                    value=[y_axis_options[0]["value"]] if y_axis_options else [],
                    style={"width": "50%"}
                ),
                dcc.Loading(
                    dcc.Graph(id=ID),
                )
            ]
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

# Callback to dynamically change y-axis
@callback(
    [Output("graph-title", "children"),
     Output(ID, "figure")],
    [Input("y-axis-dropdown", "value")]
)
def customizable_graph(y_axis_variable):
    if not y_axis_variable:
        return "No data selected", {}

    graph_title = f"{', '.join(y_axis_variable)} vs Time (sec)"

    fig = px.line(
        df,
        x="timestamp",
        y=y_axis_variable,
        labels={"timestamp": "Time"}
    )
    fig.update_layout(title=graph_title)
    return graph_title, fig
