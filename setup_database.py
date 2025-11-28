import sqlite3
from datetime import datetime, timedelta
import os

# Database filename
DB_FILE = "customer_service.db"

def create_database():
    """
    Create the database.

    Why? We need to create structure for the database before we can populate it with data.
    """

    # delete old database if it exists
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Old database deleted: {DB_FILE}")

    # connect to database (create file if it doesn't exist)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    print(f"New database created: {DB_FILE}")

    # CUSTOMERS TABLE
    cursor.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT NOT NULL,
            email   TEXT,
            phone   TEXT,
            status  TEXT DEFAULT 'active',
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)    
    print("✅Customers table created")

    # TICKETS TABLE
    cursor.execute("""
        CREATE TABLE tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            issue TEXT NOT NULL,
            status  TEXT DEFAULT 'open',
            priority TEXT DEFAULT 'medium',
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    """)
    print("✅Tickets table created")

    #save changes
    conn.commit()
    return conn, cursor

def add_sample_data(cursor, conn):
    print("Adding sample data to database...")

    # sample customers
    customers = [
        ("Alice Johnson", "alice@email.com", "555-0101", "active"),
        ("Bob Smith", "bob@email.com", "555-0102", "active"),
        ("Charlie Brown", "charlie@email.com", "555-0103", "active"),
        ("Diana Prince", "diana@email.com", "555-0104", "disabled"),
        ("Eve Martinez", "eve@email.com", "555-0105", "active"),
    ]

    # Insert customers into the database
    cursor.executemany("INSERT INTO customers (name, email, phone, status) VALUES (?, ?, ?, ?)", customers)
    print(f" Added {len(customers)} customers")

    # Sample tickets
    tickets = [
        (1, "Cannot login to my account", "open", "medium"),
        (1, "My account is not working", "open", "high"),
        (2, "Need help upgrading subscription", "in_progress", "low"),
        (3, "Billing issue - charged twice", "open", "high"),
        (4, "Feature request: dark mode", "open", "low"),
        (5, "Password reset not working", "resolved", "medium"),
    ]

    # Insert tickets into the database
    cursor.executemany("INSERT INTO tickets (customer_id, issue, status, priority) VALUES (?, ?, ?, ?)", tickets)
    print(f" Added {len(tickets)} tickets")

    #save changes
    conn.commit()

def verify_database(cursor):
    """ Print database contents to verify it worked """

    print("\n","="*60)
    print("DATABASE CONTENTS")
    print("="*60)

    # show customers
    print("\nCustomers:")
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()

    for customer in customers:
        print(customer, "\n")
        print(f"  ID {customer[0]}: {customer[1]} ({customer[4]})")

    # show tickets
    print("\nTICKETS:")
    cursor.execute(""" 
        SELECT t.id, c.name, t.issue, t.status, t.priority, t.created_at
        FROM tickets t
        JOIN customers c ON t.customer_id = c.id
    """)
    tickets = cursor.fetchall()

    for ticket in tickets:
        print(f"   Ticket #{ticket[0]} - {ticket[1]}: {ticket[2]} [{ticket[3]} {ticket[4]}]")

    print("\n" + "="*60)

def main():
    """ Main function to set up everything """
    print(" Setting up custmer service database\n")

    # create database
    conn, cursor = create_database()

    # add sample data
    add_sample_data(cursor, conn)

    # verify database
    verify_database(cursor)

    # close connection
    conn.close()
    print("Database setup complete")
    print(f"Database saved as: {DB_FILE}")

if __name__ == "__main__":
    main()