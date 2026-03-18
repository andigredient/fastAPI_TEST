
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from main import app
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import app.database as db_module

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://postgres:358899aA%21@localhost:5432/test_db")

@pytest.fixture(scope="session")
def test_connection():
    conn = psycopg2.connect(TEST_DATABASE_URL, cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS links (
        id SERIAL PRIMARY KEY,              -- айди
        original_url TEXT NOT NULL,         -- оригинальная ссылка
        short_code TEXT UNIQUE NOT NULL,    -- короткая ссылка
        clicks INTEGER DEFAULT 0,           -- количество кликов
        created_at TIMESTAMP DEFAULT NOW(), -- дата создания
        last_accessed TIMESTAMP,            -- последний заход
        expires_at TIMESTAMP                -- срок годности
        )
    """)
    conn.commit()
    cursor.close()
    
    yield conn
    conn.close()

@pytest.fixture(autouse=True)
def override_and_cleanup(test_connection):

    original_connection = db_module.connection
    original_get_cursor = db_module.get_cursor
    
    db_module.connection = test_connection
    db_module.get_cursor = lambda: test_connection.cursor()

    cursor = test_connection.cursor()
    cursor.execute("TRUNCATE TABLE links RESTART IDENTITY CASCADE")
    test_connection.commit()
    cursor.close()    
    yield
    
    db_module.connection = original_connection
    db_module.get_cursor = original_get_cursor

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest.fixture
def db_cursor(test_connection):
    cursor = test_connection.cursor()
    yield cursor
    cursor.close()