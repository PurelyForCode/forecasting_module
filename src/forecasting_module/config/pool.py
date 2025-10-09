import os 
from psycopg_pool import ConnectionPool
from dotenv import load_dotenv

# Load .env file (only needed locally)
load_dotenv()

# Build the connection string from env vars
DATABASE_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# Create the connection pool
pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=int(os.getenv("DB_MIN_CONN", 1)),
    max_size=int(os.getenv("DB_MAX_CONN", 10)),
    num_workers=3,  # optional
    timeout=10,     # seconds
)

# Example: get a connection from the pool
def get_all_users():
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, username FROM users;")
            return cur.fetchall()

if __name__ == "__main__":
    users = get_all_users()
    for user in users:
        print(user)
