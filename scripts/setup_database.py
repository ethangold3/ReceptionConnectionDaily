import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Get the DATABASE_URL from Heroku's environment variables
DATABASE_URL = os.environ['DATABASE_URL']

def setup_database():
    # Connect to the default database
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Create the daily_players table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_players (
        date DATE PRIMARY KEY,
        start_player TEXT NOT NULL,
        end_player TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("Database setup complete.")

if __name__ == "__main__":
    setup_database()