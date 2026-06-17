import sqlite3
from datetime import date, timedelta
import random

DB_NAME = "personal_finance.db"

categories = [
    "Food",
    "Transport",
    "Shopping",
    "Entertainment",
    "Bills",
    "Salary",
    "Freelance",
    "Health"
]

payment_methods = [
    "UPI",
    "Cash",
    "Credit Card",
    "Debit Card",
    "Bank Transfer"
]

try:
    # Connect to SQLite database
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    print("Database connection established")

    # Drop existing table
    cursor.execute("DROP TABLE IF EXISTS transactions")

    # Create table
    cursor.execute("""
    CREATE TABLE transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL,
        category VARCHAR(30) NOT NULL,
        type VARCHAR(30) NOT NULL,
        amount REAL NOT NULL,
        description VARCHAR(100),
        payment_method VARCHAR(30) NOT NULL
    )
    """)

    print("Table created successfully")

    # Generate seed data
    data = []
    start_date = date(2026, 1, 1)

    for i in range(200):
        txn_date = start_date + timedelta(days=i % 180)

        category = random.choice(categories)

        if category in ["Salary", "Freelance"]:
            txn_type = "Income"
            amount = round(random.uniform(5000, 50000), 2)
        else:
            txn_type = "Expense"
            amount = round(random.uniform(50, 5000), 2)

        description = f"{category} transaction #{i + 1}"
        payment_method = random.choice(payment_methods)

        data.append(
            (
                txn_date.isoformat(),
                category,
                txn_type,
                amount,
                description,
                payment_method
            )
        )

    # Insert data
    cursor.executemany("""
    INSERT INTO transactions
    (date, category, type, amount, description, payment_method)
    VALUES (?, ?, ?, ?, ?, ?)
    """, data)

    connection.commit()

    print(f"{len(data)} rows inserted successfully")

    # Verify insert count
    cursor.execute("SELECT COUNT(*) FROM transactions")
    total_rows = cursor.fetchone()[0]

    print(f"Total rows in table: {total_rows}")

except sqlite3.Error as e:
    print(f"SQLite Error: {e}")

finally:
    if 'connection' in locals():
        connection.close()
        print("Database connection closed")