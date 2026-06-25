import sqlite3
from datetime import date, timedelta
import random

DB_NAME = "library_book_lending_agent/library_database.db"

TODAY = date(2026, 6, 23)

BOOKS = [
    ("BK001", "Dune", "Frank Herbert", "sci-fi", 3, 2, 18.99),
    ("BK002", "1984", "George Orwell", "fiction", 4, 3, 12.99),
    ("BK003", "Sapiens", "Yuval Noah Harari", "non-fiction", 2, 2, 22.00),
    ("BK004", "Atomic Habits", "James Clear", "self-help", 2, 0, 19.99),
    ("BK005", "The Pragmatic Programmer", "Hunt & Thomas", "tech", 3, 3, 34.99),
    ("BK006", "The Great Gatsby", "F. Scott Fitzgerald", "fiction", 5, 5, 10.99),
    ("BK007", "Clean Code", "Robert C. Martin", "tech", 4, 3, 29.99),
    ("BK008", "The Alchemist", "Paulo Coelho", "fiction", 3, 2, 14.99),
    ("BK009", "Thinking, Fast and Slow", "Daniel Kahneman", "non-fiction", 2, 1, 24.99),
    ("BK010", "The Hobbit", "J.R.R. Tolkien", "fiction", 4, 4, 13.99),
    ("BK011", "Brave New World", "Aldous Huxley", "fiction", 3, 2, 11.99),
    ("BK012", "Deep Work", "Cal Newport", "self-help", 2, 2, 16.99),
    ("BK013", "The Lean Startup", "Eric Ries", "tech", 3, 3, 21.99),
    ("BK014", "Foundation", "Isaac Asimov", "sci-fi", 2, 1, 15.99),
    ("BK015", "Neuromancer", "William Gibson", "sci-fi", 2, 2, 13.99),
    ("BK016", "Harry Potter and the Sorcerer's Stone", "J.K. Rowling", "fiction", 5, 4, 12.99),
    ("BK017", "To Kill a Mockingbird", "Harper Lee", "fiction", 4, 3, 11.99),
    ("BK018", "The Power of Habit", "Charles Duhigg", "self-help", 3, 2, 17.99),
    ("BK019", "Python Crash Course", "Eric Matthes", "tech", 4, 4, 32.99),
    ("BK020", "The Martian", "Andy Weir", "sci-fi", 3, 2, 16.99),
]

MEMBERS = [
    ("M001", "Alice Johnson", "alice.johnson@email.com", 1),
    ("M002", "Bob Smith", "bob.smith@email.com", 1),
    ("M003", "Carol Davis", "carol.davis@email.com", 0),
    ("M004", "Dave Wilson", "dave.wilson@email.com", 0),
    ("M005", "Eve Martinez", "eve.martinez@email.com", 2),
    ("M006", "Frank Brown", "frank.brown@email.com", 1),
    ("M007", "Grace Lee", "grace.lee@email.com", 0),
    ("M008", "Henry Taylor", "henry.taylor@email.com", 2),
    ("M009", "Isla Anderson", "isla.anderson@email.com", 1),
    ("M010", "Jack Thomas", "jack.thomas@email.com", 0),
]

def make_txn_id(n):
    return f"TXN{n:03d}"

def gen_transactions():
    txns = []
    txn_counter = 1

    # Seed in-flight checkouts to match active_checkouts in MEMBERS
    in_flight = [
        # (member_id, book_id, checkout_date_offset, due_date_offset)
        ("M001", "BK001", -10, 4),    # Alice has Dune, due in 4 days
        ("M002", "BK002", -5,  9),    # Bob has 1984, due in 9 days
        ("M004", "BK004", -20, -6),   # Dave had Atomic Habits (this becomes closed below)
        ("M005", "BK007", -3,  11),   # Eve has Clean Code
        ("M005", "BK009", -7,  7),    # Eve has Thinking Fast and Slow
        ("M006", "BK008", -12, 2),    # Frank has The Alchemist
        ("M008", "BK014", -8,  6),    # Henry has Foundation
        ("M008", "BK011", -15, -1),   # Henry has Brave New World (overdue by 1 day)
        ("M009", "BK020", -4,  10),   # Isla has The Martian
    ]

    for member_id, book_id, co_offset, due_offset in in_flight:
        checkout_date = (TODAY + timedelta(days=co_offset)).isoformat()
        due_date = (TODAY + timedelta(days=due_offset)).isoformat()
        txns.append((
            make_txn_id(txn_counter), member_id, book_id,
            "checkout", checkout_date, due_date, 0.0, "open"
        ))
        txn_counter += 1

    # Reservation: M003 reserved Atomic Habits (BK004, out of stock)
    txns.append((
        make_txn_id(txn_counter), "M003", "BK004",
        "reservation", (TODAY + timedelta(days=-2)).isoformat(), None, 0.0, "reserved"
    ))
    txn_counter += 1

    # Historical closed checkouts and returns (to reach ~200 total records)
    historical_checkouts = [
        # (member_id, book_id, days_ago_checkout, checkout_duration, was_overdue_by)
        ("M001", "BK006", 60, 14, 0),
        ("M001", "BK010", 55, 14, 0),
        ("M001", "BK016", 50, 14, 2),   # 2 days overdue
        ("M001", "BK019", 45, 14, 0),
        ("M001", "BK003", 40, 14, 0),
        ("M001", "BK013", 35, 14, 0),
        ("M001", "BK005", 30, 14, 0),
        ("M001", "BK015", 25, 14, 1),   # 1 day overdue
        ("M001", "BK018", 20, 14, 0),
        ("M002", "BK001", 90, 14, 0),
        ("M002", "BK005", 85, 14, 0),
        ("M002", "BK007", 80, 14, 3),   # 3 days overdue
        ("M002", "BK010", 75, 14, 0),
        ("M002", "BK011", 70, 14, 0),
        ("M002", "BK013", 65, 14, 0),
        ("M002", "BK014", 60, 14, 0),
        ("M002", "BK016", 55, 14, 0),
        ("M002", "BK020", 50, 14, 0),
        ("M002", "BK006", 45, 14, 0),
        ("M003", "BK002", 100, 14, 0),
        ("M003", "BK005", 95, 14, 0),
        ("M003", "BK008", 90, 14, 5),   # 5 days overdue
        ("M003", "BK009", 85, 14, 0),
        ("M003", "BK010", 80, 14, 0),
        ("M003", "BK013", 75, 14, 0),
        ("M003", "BK016", 70, 14, 0),
        ("M003", "BK018", 65, 14, 0),
        ("M003", "BK019", 60, 14, 0),
        ("M004", "BK001", 80, 14, 0),
        ("M004", "BK003", 75, 14, 0),
        ("M004", "BK006", 70, 14, 2),
        ("M004", "BK007", 65, 14, 0),
        ("M004", "BK012", 60, 14, 0),
        ("M004", "BK013", 55, 14, 0),
        ("M004", "BK015", 50, 14, 0),
        ("M004", "BK017", 45, 14, 0),
        ("M004", "BK019", 40, 14, 0),
        ("M004", "BK020", 35, 14, 0),
        ("M005", "BK001", 120, 14, 0),
        ("M005", "BK002", 115, 14, 0),
        ("M005", "BK005", 110, 14, 0),
        ("M005", "BK006", 105, 14, 0),
        ("M005", "BK010", 100, 14, 4),
        ("M005", "BK013", 95, 14, 0),
        ("M005", "BK014", 90, 14, 0),
        ("M005", "BK015", 85, 14, 0),
        ("M005", "BK018", 80, 14, 0),
        ("M005", "BK019", 75, 14, 0),
        ("M006", "BK002", 110, 14, 0),
        ("M006", "BK003", 105, 14, 0),
        ("M006", "BK004", 100, 14, 0),
        ("M006", "BK005", 95, 14, 0),
        ("M006", "BK007", 90, 14, 0),
        ("M006", "BK010", 85, 14, 3),
        ("M006", "BK011", 80, 14, 0),
        ("M006", "BK016", 75, 14, 0),
        ("M006", "BK017", 70, 14, 0),
        ("M006", "BK019", 65, 14, 0),
        ("M007", "BK001", 90, 14, 0),
        ("M007", "BK002", 85, 14, 0),
        ("M007", "BK004", 80, 14, 0),
        ("M007", "BK006", 75, 14, 0),
        ("M007", "BK008", 70, 14, 0),
        ("M007", "BK011", 65, 14, 2),
        ("M007", "BK013", 60, 14, 0),
        ("M007", "BK015", 55, 14, 0),
        ("M007", "BK017", 50, 14, 0),
        ("M007", "BK020", 45, 14, 0),
        ("M008", "BK002", 95, 14, 0),
        ("M008", "BK003", 90, 14, 0),
        ("M008", "BK005", 85, 14, 0),
        ("M008", "BK006", 80, 14, 0),
        ("M008", "BK007", 75, 14, 6),
        ("M008", "BK010", 70, 14, 0),
        ("M008", "BK012", 65, 14, 0),
        ("M008", "BK013", 60, 14, 0),
        ("M008", "BK015", 55, 14, 0),
        ("M008", "BK016", 50, 14, 0),
        ("M009", "BK001", 130, 14, 0),
        ("M009", "BK003", 125, 14, 0),
        ("M009", "BK005", 120, 14, 0),
        ("M009", "BK006", 115, 14, 0),
        ("M009", "BK007", 110, 14, 0),
        ("M009", "BK009", 105, 14, 0),
        ("M009", "BK010", 100, 14, 0),
        ("M009", "BK011", 95, 14, 3),
        ("M009", "BK013", 90, 14, 0),
        ("M009", "BK018", 85, 14, 0),
        ("M010", "BK002", 140, 14, 0),
        ("M010", "BK004", 135, 14, 0),
        ("M010", "BK005", 130, 14, 0),
        ("M010", "BK006", 125, 14, 0),
        ("M010", "BK007", 120, 14, 0),
        ("M010", "BK009", 115, 14, 0),
        ("M010", "BK012", 110, 14, 2),
        ("M010", "BK015", 105, 14, 0),
        ("M010", "BK017", 100, 14, 0),
        ("M010", "BK019", 95, 14, 0),
    ]

    # Price lookup for fine calculation
    price_map = {b[0]: b[6] for b in BOOKS}

    for member_id, book_id, days_ago, duration, overdue_by in historical_checkouts:
        checkout_date = TODAY - timedelta(days=days_ago)
        due_date = checkout_date + timedelta(days=duration)
        return_date = due_date + timedelta(days=overdue_by)

        fine = 0.0
        if overdue_by > 0:
            price = price_map.get(book_id, 15.0)
            fine = round(overdue_by * 0.01 * price, 2)

        # Checkout record
        txns.append((
            make_txn_id(txn_counter), member_id, book_id,
            "checkout", checkout_date.isoformat(), due_date.isoformat(), 0.0, "closed"
        ))
        txn_counter += 1

        # Return record
        txns.append((
            make_txn_id(txn_counter), member_id, book_id,
            "return", return_date.isoformat(), due_date.isoformat(), fine, "closed"
        ))
        txn_counter += 1

    return txns


try:
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    print("Database connection established")

    # --- catalog ---
    cursor.execute("DROP TABLE IF EXISTS transactions")
    cursor.execute("DROP TABLE IF EXISTS catalog")
    cursor.execute("DROP TABLE IF EXISTS members")

    cursor.execute("""
    CREATE TABLE catalog (
        book_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        genre TEXT,
        total_copies INTEGER,
        available_copies INTEGER,
        price_value REAL NOT NULL
    );
    """)
    cursor.executemany(
        "INSERT INTO catalog VALUES (?, ?, ?, ?, ?, ?, ?)",
        BOOKS
    )
    print(f"{len(BOOKS)} books inserted into catalog")

    # --- members ---
    cursor.execute("""
    CREATE TABLE members (
        member_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        active_checkouts INTEGER DEFAULT 0 CHECK (active_checkouts >= 0 AND active_checkouts <= 3)
    );
    """)
    cursor.executemany(
        "INSERT INTO members VALUES (?, ?, ?, ?)",
        MEMBERS
    )
    print(f"{len(MEMBERS)} members inserted")

    # --- transactions ---
    cursor.execute("""
    CREATE TABLE transactions (
        txn_id TEXT PRIMARY KEY,
        member_id TEXT NOT NULL,
        book_id TEXT NOT NULL,
        txn_type TEXT NOT NULL CHECK (txn_type IN ('checkout', 'return', 'reservation')),
        date TEXT NOT NULL,
        due_date TEXT,
        fine REAL DEFAULT 0.0,
        status TEXT NOT NULL CHECK (status IN ('open', 'closed', 'reserved')),
        FOREIGN KEY (member_id) REFERENCES members(member_id),
        FOREIGN KEY (book_id) REFERENCES catalog(book_id)
    );
    """)

    transactions = gen_transactions()
    cursor.executemany(
        "INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        transactions
    )
    print(f"{len(transactions)} transactions inserted")

    connection.commit()

    # Verification
    for table in ["catalog", "members", "transactions"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count} rows")

except sqlite3.Error as e:
    print(f"SQLite Error: {e}")

finally:
    if 'connection' in locals():
        connection.close()
        print("Database connection closed")
