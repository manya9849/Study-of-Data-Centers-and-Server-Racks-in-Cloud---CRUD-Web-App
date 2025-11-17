import sqlite3

def create_db():
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()

    # Enable foreign key support
    cur.execute("PRAGMA foreign_keys = ON;")

    # -------------------- DATACENTERS --------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS datacenters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT NOT NULL
    )
    """)

    # -------------------- RACKS --------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS racks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        datacenter_id INTEGER NOT NULL,
        rack_name TEXT NOT NULL,
        capacity INTEGER NOT NULL,
        FOREIGN KEY (datacenter_id) REFERENCES datacenters(id)
            ON DELETE CASCADE ON UPDATE CASCADE
    )
    """)

    # -------------------- SERVERS --------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS servers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rack_id INTEGER NOT NULL,
        server_name TEXT NOT NULL,
        cpu_usage INTEGER NOT NULL,
        temperature INTEGER NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (rack_id) REFERENCES racks(id)
            ON DELETE CASCADE ON UPDATE CASCADE
    )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_db()
