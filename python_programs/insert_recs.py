import os
import sqlite3
import importlib.util
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except Exception:
    psycopg2 = None

# Load users list from the local users.py (supports variable name users or users_data)
def load_users():
    users_file = os.path.join(os.path.dirname(__file__), 'users.py')
    spec = importlib.util.spec_from_file_location('local_users', users_file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, 'users', None) or getattr(mod, 'users_data', None) or []


def main():
    DATABASE_URL = os.environ.get('DATABASE_URL')
    users = load_users()

    if DATABASE_URL and psycopg2 is not None:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        for user in users:
            # avoid duplicates by username
            cur.execute("SELECT user_id FROM users WHERE username = %s", (user.get('username'),))
            if cur.fetchone() is None:
                cur.execute("INSERT INTO users (username, password, auth_level) VALUES (%s, %s, %s)",
                            (user.get('username'), user.get('password'), user.get('auth_level')))
        conn.commit()
        conn.close()
        print('Postgres: Data inserted successfully.')
        return

    # Fallback to sqlite
    conn = sqlite3.connect('people.db')
    cursor = conn.cursor()

    for user in users:
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user.get('user_id'),))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO users (user_id, username, password, auth_level) VALUES (?, ?, ?, ?)",
                           (user.get('user_id'), user.get('username'), user.get('password'), user.get('auth_level')))

    conn.commit()
    conn.close()

    print('SQLite: Data inserted successfully.')


if __name__ == '__main__':
    main()