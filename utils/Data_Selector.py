import os
import psycopg2

# PostgreSQL database URL
DB_URL = ''

# PostgreSQL connection setup
def get_db():
    """Establish and return a PostgreSQL database connection."""
    try:
        connection = psycopg2.connect(DB_URL)
        return connection
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def fetch_metrics_in_time_range(start_time, end_time):
    """Fetch data from PostgreSQL table 'vehicle_data' within the specified time range."""
    connection = get_db()
    if connection is None:
        return {"error": "Failed to connect to PostgreSQL"}

    try:
        cursor = connection.cursor()

        # Query to fetch metrics within the specified time range
        query = """
        SELECT brand, model, year 
        FROM vehicle_data
        WHERE timestamp >= %s AND timestamp <= %s;
        """
        cursor.execute(query, (start_time, end_time))
        records = cursor.fetchall()

        if records:
            columns = ["brand", "model", "year"]
            data = [dict(zip(columns, row)) for row in records]
            return {"data": data}
        else:
            return {"data": "No data found in PostgreSQL within the specified time range"}
    except Exception as e:
        return {"error": f"Error fetching data from PostgreSQL: {e}"}
    finally:
        cursor.close()
        connection.close()

def fetch_from_local_files():
    """Fetch data from a local file."""
    try:
        with open("local_data.txt", "r") as file:
            return {"data": file.read()}
    except FileNotFoundError:
        return {"error": "Local file not found"}

def fetch_from_pe3_dump():
    """Fetch data from a PE3 dump CSV file."""
    try:
        with open("pe3_dump.csv", "r") as file:
            return {"data": file.read()}
    except FileNotFoundError:
        return {"error": "PE3 Dump file not found"}

class DataSourceManager:
    """Manages different data sources and fetches data accordingly."""
    def __init__(self):
        self.data_source = "PostgreSQL"  # Default data source

    def set_data_source(self, source):
        if source in ["PostgreSQL", "Local Files", "PE3 Dump"]:
            self.data_source = source
        else:
            raise ValueError("Invalid data source")

    def get_data(self, start_time=None, end_time=None):
        if self.data_source == 'PostgreSQL' and start_time and end_time:
            return fetch_metrics_in_time_range(start_time, end_time)
        elif self.data_source == 'Local Files':
            return fetch_from_local_files()
        elif self.data_source == 'PE3 Dump':
            return fetch_from_pe3_dump()
        else:
            return {"error": "No valid data source selected"}

if __name__ == '__main__':
    data_manager = DataSourceManager()
    
    start_time = "2024-04-23 13:40:29"
    end_time = "2024-04-23 13:56:41"
    
    while True:
        print("\nCurrent Data Source:", data_manager.data_source)
        print("Choose Data Source: 1 - PostgreSQL, 2 - Local Files, 3 - PE3 Dump")
        choice = input("Enter the number to select data source (or 'q' to quit): ")

        if choice == 'q':
            break
        elif choice == '1':
            data_manager.set_data_source('PostgreSQL')
        elif choice == '2':
            data_manager.set_data_source('Local Files')
        elif choice == '3':
            data_manager.set_data_source('PE3 Dump')
        else:
            print("Invalid selection. Please try again.")
            continue

        if data_manager.data_source == 'PostgreSQL':
            data = data_manager.get_data(start_time, end_time)
        else:
            data = data_manager.get_data()

        print("\nFetched Data:", data)
