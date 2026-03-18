from datetime import datetime, timedelta
from app.database import *

def test_add_and_find_link(db_cursor):
    add_link("https://test.com", "abc123", datetime.now() + timedelta(days=5))
    assert find_link_short("abc123") == "https://test.com"
    assert find_link_original("https://test.com") == "abc123"

def test_delete_link(db_cursor):
    add_link("https://test.com", "del123", datetime.now() + timedelta(days=5))
    delete_link("del123")
    assert find_link_short("del123") is None

def test_following_links(db_cursor):
    add_link("https://test.com", "click123", datetime.now() + timedelta(days=5))
    stats_before = get_stats_db("click123")
    following_links("click123")
    stats_after = get_stats_db("click123")
    assert stats_after['clicks'] == stats_before['clicks'] + 1

def test_update_url_db(db_cursor):
    add_link("https://test.com", "old123", datetime.now() + timedelta(days=5))
    update_url_db("new123", "old123")
    assert find_link_short("old123") is None
    assert find_link_short("new123") == "https://test.com"

def test_delete_expired_links(db_cursor):
    add_link("https://expired.com", "exp123", datetime.now() - timedelta(days=1))
    add_link("https://active.com", "act123", datetime.now() + timedelta(days=1))
    delete_expired_links()
    assert find_link_short("exp123") is None
    assert find_link_short("act123") == "https://active.com"

def test_create_table(mocker):
    mock_cursor = mocker.MagicMock()
    mocker.patch('app.database.get_cursor', return_value=mock_cursor)
    mocker.patch('app.database.connection')    
    create_table()
    mock_cursor.execute.assert_called_once()
    mock_cursor.close.assert_called_once()

def test_delete_last_accessed_links(db_cursor):    
    add_link("https://old.com", "old123", datetime.now() + timedelta(days=5))    
    db_cursor.execute("""
        UPDATE links 
        SET last_accessed = '2020-01-01' 
        WHERE short_code = 'old123'
    """)    
    deleted = delete_last_accessed_links()
    assert isinstance(deleted, list)

def test_find_link_short_error(mocker):
    mock_cursor = mocker.MagicMock()
    mock_cursor.execute.side_effect = Exception("DB Error")
    mocker.patch('app.database.get_cursor', return_value=mock_cursor)    
    result = find_link_short("test")
    assert result is None

def test_find_link_original_error(mocker):
    mock_cursor = mocker.MagicMock()
    mock_cursor.execute.side_effect = Exception("DB Error")
    mocker.patch('app.database.get_cursor', return_value=mock_cursor)
    result = find_link_original("https://test.com")
    assert result is None

def test_delete_link_error(mocker):
    mock_cursor = mocker.MagicMock()
    mock_cursor.execute.side_effect = Exception("DB Error")
    mocker.patch('app.database.get_cursor', return_value=mock_cursor)    
    result = delete_link("test")
    assert result is None

def test_get_stats_db_error(mocker):
    mock_cursor = mocker.MagicMock()
    mock_cursor.execute.side_effect = Exception("DB Error")
    mocker.patch('app.database.get_cursor', return_value=mock_cursor)    
    result = get_stats_db("test")
    assert result is None

def test_update_url_db_error(mocker):
    mock_cursor = mocker.MagicMock()
    mock_cursor.execute.side_effect = Exception("DB Error")
    mocker.patch('app.database.get_cursor', return_value=mock_cursor)    
    result = update_url_db("new", "old")
    assert result is None