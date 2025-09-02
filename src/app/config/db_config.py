import os
from dotenv import load_dotenv
from psycopg2 import pool

load_dotenv()

def get_env_var(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise EnvironmentError(f"Missing required environment variable: {name}")
    return value


pg_pool = pool.SimpleConnectionPool(
    1,
    10,
    dbname=get_env_var("DB_NAME"),
    user=get_env_var("DB_USER"),
    password=get_env_var("DB_PASSWORD"),
    host=get_env_var("DB_HOST"),
    port=get_env_var("DB_PORT"),
)



