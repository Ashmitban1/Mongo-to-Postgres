from flask import Flask, g
import psycopg2
import os

app = Flask(__name__)

# Database connection URL (update if needed)
DB_URL = ''

def get_db():
    """Establish and return a PostgreSQL database connection."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = psycopg2.connect(DB_URL)
    return db

def close_db(e=None):
    """Close the database connection."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.teardown_appcontext
def teardown_db(exception):
    close_db()

def get_data(session_id, start_time, end_time):
    """Fetch metrics for the given session ID within the specified time range."""
    db = get_db()
    cursor = db.cursor()

    # SQL query to fetch data within the time range
    query = """
    SELECT brand, model, year
    FROM realtime_metrics
    WHERE session_id = %s
      AND timestamp BETWEEN %s AND %s;
    """

    # Execute the query with parameters
    cursor.execute(query, (session_id, start_time, end_time))
    results = cursor.fetchall()

    # Convert results to a list of dictionaries
    columns = ['brand', 'model', 'year']
    data = [dict(zip(columns, row)) for row in results]

    cursor.close()
    return data

# Example route for testing
@app.route('/metrics/<session_id>')
def metrics(session_id):
    start_time = '2024-04-23 13:40:29'
    end_time = '2024-04-23 13:56:41'
    data = get_data(session_id, start_time, end_time)
    return {'data': data}

if __name__ == '__main__':
    app.run(debug=True)
