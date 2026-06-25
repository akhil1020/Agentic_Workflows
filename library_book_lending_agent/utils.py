import sqlite3
import random
import pandas as pd

# db_path = "library_book_lending_agent/library_database.db"

def execute_sql(query: str) -> pd.DataFrame:
    """
    Execute any SELECT over the event-sourced 'transactions' table.
    """
    db_path = "library_database.db"
    q = query.strip().removeprefix("```sql").removesuffix("```").strip()
    conn = sqlite3.connect(db_path)
    try:
        return pd.read_sql_query(q, conn)
    except Exception as e:
        return pd.DataFrame({"error": [str(e)]})
    finally:
        conn.close()