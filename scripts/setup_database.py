import sqlite3
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(project_root, "data", "daily_players.db")

def setup_database():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_players (
        date TEXT PRIMARY KEY,
        start_player TEXT NOT NULL,
        end_player TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()
    
    print("Database setup complete.")

if __name__ == "__main__":
    setup_database()