import sqlite3
from faker import Faker
from datetime import datetime, timedelta
import random

# Инициализация Faker
fake = Faker('ru_RU')

# Создание базы данных и таблиц

def create_database_schema(db_name='library.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Создаем таблицу Книги
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        genre TEXT NOT NULL,
        year INTEGER NOT NULL
    )
    ''')
    
    # Создаем таблицу Читатели
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Readers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        contact TEXT NOT NULL,
        membership_status TEXT NOT NULL
    )
    ''')
    
    # Создаем таблицу Выдачи книг
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS BookIssues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,
        reader_id INTEGER NOT NULL,
        issue_date DATE NOT NULL,
        return_date DATE,
        FOREIGN KEY (book_id) REFERENCES Books(id),
        FOREIGN KEY (reader_id) REFERENCES Readers(id)
    )
    ''')
    
    conn.commit()
    return conn

# Генерация тестовых данных

def generate_fake_data():
    # Списки для генерации данных
    genres = [
        'Роман', 'Детектив', 'Фантастика', 'Фэнтези', 'Исторический',
        'Биография', 'Научная литература', 'Поэзия', 'Драма', 'Учебник'
    ]
    statuses = ['Активен', 'Приостановлен', 'Просрочен', 'Новый']
    
    # Генерация книг
    books = []
    for _ in range(100):
        books.append({
            'title': fake.catch_phrase(),
            'author': fake.name(),
            'genre': random.choice(genres),
            'year': random.randint(1950, 2023)
        })
    
    # Генерация читателей
    readers = []
    for _ in range(50):
        readers.append({
            'full_name': fake.name(),
            'contact': fake.email(),
            'membership_status': random.choice(statuses)
        })
    
    return books, readers

def populate_database(conn, books, readers):
    cursor = conn.cursor()
    
    # Заполняем книги
    for book in books:
        cursor.execute('''
        INSERT INTO Books (title, author, genre, year)
        VALUES (?, ?, ?, ?)
        ''', (book['title'], book['author'], book['genre'], book['year']))
    
    # Заполняем читателей
    for reader in readers:
        cursor.execute('''
        INSERT INTO Readers (full_name, contact, membership_status)
        VALUES (?, ?, ?)
        ''', (reader['full_name'], reader['contact'], reader['membership_status']))
    
    # Генерируем выдачи книг
    for _ in range(200):
        book_id = random.randint(1, len(books))
        reader_id = random.randint(1, len(readers))
        issue_date = fake.date_between(start_date='-1y', end_date='today')
        
        # 70% книг возвращены
        if random.random() < 0.7:
            return_date = issue_date + timedelta(days=random.randint(1, 60))
        else:
            return_date = None
        
        cursor.execute('''
        INSERT INTO BookIssues (book_id, reader_id, issue_date, return_date)
        VALUES (?, ?, ?, ?)
        ''', (book_id, reader_id, issue_date, return_date))
    
    conn.commit()

# SQL-запросы к базе данных

def execute_queries(conn):
    cursor = conn.cursor()
    
    print("\n1. 5 самых популярных книг:")
    cursor.execute('''
    SELECT b.title, b.author, COUNT(*) AS issue_count
    FROM BookIssues bi
    JOIN Books b ON bi.book_id = b.id
    GROUP BY b.id
    ORDER BY issue_count DESC
    LIMIT 5
    ''')
    print("{:<40} {:<25} {:<10}".format("Название", "Автор", "Выдач"))
    for row in cursor.fetchall():
        print("{:<40} {:<25} {:<10}".format(row[0], row[1], row[2]))
    
    print("\n2. Читатели с просроченными книгами:")
    cursor.execute('''
    SELECT r.full_name, b.title, bi.issue_date
    FROM BookIssues bi
    JOIN Readers r ON bi.reader_id = r.id
    JOIN Books b ON bi.book_id = b.id
    WHERE bi.return_date IS NULL 
    AND julianday('now') - julianday(bi.issue_date) > 30
    ''')
    print("{:<30} {:<40} {:<15}".format("Читатель", "Книга", "Дата выдачи"))
    for row in cursor.fetchall():
        print("{:<30} {:<40} {:<15}".format(row[0], row[1], row[2]))
    
    print("\n3. Статистика по жанрам:")
    cursor.execute('''
    SELECT genre, COUNT(*) AS book_count, 
    (SELECT COUNT(*) FROM BookIssues bi WHERE bi.book_id = b.id) AS issue_count
    FROM Books b
    GROUP BY genre
    ORDER BY issue_count DESC
    ''')
    print("{:<20} {:<15} {:<15}".format("Жанр", "Книг", "Выдач"))
    for row in cursor.fetchall():
        print("{:<20} {:<15} {:<15}".format(row[0], row[1], row[2]))
    
    print("\n4. Самые активные читатели:")
    cursor.execute('''
    SELECT r.full_name, r.membership_status, COUNT(*) AS books_issued
    FROM BookIssues bi
    JOIN Readers r ON bi.reader_id = r.id
    GROUP BY r.id
    ORDER BY books_issued DESC
    LIMIT 5
    ''')
    print("{:<30} {:<15} {:<15}".format("Читатель", "Статус", "Книг выдано"))
    for row in cursor.fetchall():
        print("{:<30} {:<15} {:<15}".format(row[0], row[1], row[2]))


def main():
    # Создаем БД
    print("Создание базы данных...")
    conn = create_database_schema()
    
    # Генерируем данные
    print("Генерация тестовых данных...")
    books, readers = generate_fake_data()
    
    # Заполняем БД
    print("Заполнение базы данных...")
    populate_database(conn, books, readers)
    
    # Выполняем запросы
    print("\nВыполнение запросов...")
    execute_queries(conn)
    
    # Закрываем соединение
    conn.close()
    print("\nГотово! База данных сохранена в файле 'library.db'")
    print("Для просмотра данных используйте DB Browser for SQLite")

if __name__ == "__main__":
    main()