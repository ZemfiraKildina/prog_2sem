import sqlite3

def create_tables(conn):
    cursor = conn.cursor()
    
    # Создание таблицы категорий
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        url TEXT NOT NULL
    )
    ''')
    
    # Создание таблицы книг
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        price REAL NOT NULL,
        category_id INTEGER NOT NULL,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )
    ''')
    conn.commit()

def insert_data(conn, books, categories):
    cursor = conn.cursor()
    
    # Вставка категорий с именованными плейсхолдерами
    cursor.executemany('''
    INSERT OR IGNORE INTO categories (id, name, url)
    VALUES (:id, :name, :url)
    ''', categories)
    
    # Вставка книг с именованными плейсхолдерами
    cursor.executemany('''
    INSERT INTO books (id, title, price, category_id)
    VALUES (:id, :title, :price, :category_id)
    ''', books)
    
    conn.commit()