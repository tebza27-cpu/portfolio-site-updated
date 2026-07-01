import os
import sqlite3
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except Exception:
    psycopg2 = None


def showRecords():
    title = "All Records From the Table Users: "
    DATABASE_URL = os.environ.get('DATABASE_URL')

    if DATABASE_URL and psycopg2 is not None:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        cur.execute("SELECT user_id, username, password, auth_level FROM users ORDER BY user_id")
        rows = cur.fetchall()
        print(title)
        for row in rows:
            if isinstance(row, dict):
                print(f"{row.get('user_id')} {row.get('username')} {row.get('password')} {row.get('auth_level')}")
            else:
                print(f"{row[0]} {row[1]} {row[2]} {row[3]}")
        conn.close()
        return

    conn = sqlite3.connect('people.db')
    cursor = conn.cursor()
    sql = "SELECT * FROM users"
    cursor.execute(sql)
    rows = cursor.fetchall()
    print(title)
    for row in rows:
        print(f"{row[0]} {row[1]} {row[2]} {row[3]}")
    conn.close()


if __name__ == '__main__':
    showRecords()