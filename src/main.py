from db import get_connection

def main():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row["name"] for row in cursor.fetchall()]

    print("ContextGrid tables:")
    for table in tables:
        print(f" - {table}")

    conn.close()

if __name__ == "__main__":
    main()
