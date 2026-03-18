import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:358899aA%21@localhost:5432/postgres")

connection = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def get_cursor():
    return connection.cursor()

def create_table():
    cursor = get_cursor()
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
    connection.commit()
    print("Таблица создана")
    cursor.close()

def add_link(original_url, short_code, expires_at):
    cursor = get_cursor()
    cursor.execute("""
        INSERT INTO links (original_url, short_code, expires_at) VALUES (%(original_url)s, %(short_code)s, %(expires_at)s)        
    """, {'original_url':original_url, 'short_code': short_code, 'expires_at': expires_at })
    connection.commit()
    cursor.close()

def find_link_short(short_code):
    cursor = get_cursor()
    try:
        cursor.execute("""
            SELECT original_url FROM links 
            WHERE short_code = %(short_code)s
        """, {'short_code': short_code})
    
        result = cursor.fetchone()
        if result:
            original_url_value = result['original_url']
        if not original_url_value:
            return None
        else:
            return original_url_value
    except Exception as e:
        connection.rollback()
        print(f"Ошибка: {e}")
        return None
    finally:
        cursor.close()
        
def find_link_original(original_url):
    cursor = get_cursor()
    try:
        cursor.execute("""
            SELECT short_code FROM links 
            WHERE original_url = %(original_url)s
        """, {'original_url': original_url})
    
        result = cursor.fetchone()
        if result:
            short_code_value = result['short_code']
        if not short_code_value:
            print("Ссылка не найдена")
            return None
        else:
            print(f"Ссылка найдена{short_code_value}")
            return short_code_value
    except Exception as e:
        connection.rollback()
        print(f"Ошибка: {e}")
        return None
    finally:
        cursor.close()
    

def delete_link(short_code):
    cursor = get_cursor()
    try:
        cursor.execute("""
            SELECT * FROM links 
            WHERE short_code = %(short_code)s
        """, {'short_code': short_code}) 

        link = cursor.fetchone()   
        if not link:
            print("Ссылка не найдена")
            return None
        else:
            print("Ссылка найдена")
            cursor.execute("""
                    DELETE FROM links 
                    WHERE short_code = %(short_code)s
                    RETURNING *
                """, {'short_code': short_code})
            
            deleted_link = cursor.fetchone()            
            connection.commit()
            print("Ссылка удалена")
            return deleted_link
    except Exception as e:
        connection.rollback()
        print(f"Ошибка: {e}")
        return None
    finally:
        cursor.close()

    

def following_links(short_code):
    cursor = get_cursor()    
    cursor.execute("""
        UPDATE links 
        SET clicks = clicks + 1, last_accessed = NOW()
        WHERE short_code = %(short_code)s
    """, {'short_code': short_code}) 
    connection.commit()

def get_stats_db(short_code):
    try:
        cursor = get_cursor()    
        cursor.execute("""
        SELECT * FROM links 
            WHERE short_code = %(short_code)s
        """, {'short_code': short_code}) 
        result = cursor.fetchone()
        if not result:
            print("Данные не найдены")
            return None
        else:
            print(f"Данные ссылки {result}")
            return result
    except Exception as e:
        connection.rollback()
        print(f"Ошибка: {e}")
        return None
    finally:
        cursor.close()


def update_url_db(new_url, short_code):
    try:
        cursor = get_cursor()  
        cursor.execute("""
                UPDATE links 
                SET short_code = %(new_url)s
                WHERE short_code = %(short_code)s
                RETURNING *
            """, {'short_code': short_code, 'new_url': new_url})
        connection.commit()
        return True
    except Exception as e:
        connection.rollback()
        print(f"Ошибка: {e}")
        return None
    finally:
        cursor.close()


def delete_expired_links():
    cursor = get_cursor()
    cursor.execute("""
            DELETE FROM links 
            WHERE expires_at IS NOT NULL 
            AND expires_at < NOW() 
            RETURNING id, short_code, original_url, expires_at
        """)
    deleted = cursor.fetchall()
    connection.commit()
    print(f"Удалено {len(deleted)} истекших ссылок")
    return deleted

def delete_last_accessed_links():
    cursor = get_cursor()
    cursor.execute("""
            DELETE FROM links 
            WHERE expires_at IS NOT NULL 
            AND last_accessed < NOW() 
            RETURNING id, short_code, original_url, expires_at
        """)
    deleted = cursor.fetchall()
    connection.commit()
    print(f"Удалено {len(deleted)} истекших ссылок с последнего входа")
    return deleted