import os
import sqlite3
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except Exception:
    psycopg2 = None


def main():
    DATABASE_URL = os.environ.get('DATABASE_URL')

    if DATABASE_URL and psycopg2 is not None:
        # Use Postgres
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                auth_level REAL NOT NULL
            );
        ''')
        conn.commit()
        conn.close()
        print('Postgres: users table ensured.')
        return

    # Fallback to sqlite for local usage
    conn = sqlite3.connect('people.db')
    cursor = conn.cursor()

    # Check if the table already exists
    cursor.execute('''
        SELECT name FROM sqlite_master WHERE type='table' AND name='users';
    ''')
    table_exists = cursor.fetchone()

    if not table_exists:
        cursor.execute('''
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                auth_level REAL NOT NULL
            );
        ''')
        print('SQLite: Table created successfully.')
    else:
        print('SQLite: Table already exists.')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()