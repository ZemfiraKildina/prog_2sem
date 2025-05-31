import sqlite3
from pypika import Query, Table, Field, functions as fn

# Инициализация таблиц
books = Table('books')
categories = Table('categories')

# 2 запроса с JOIN
def join_query_1():
    return Query \
        .from_(books) \
        .join(categories) \
        .on(books.category_id == categories.id) \
        .select(
            books.title,
            categories.name.as_('category'),
            books.price
        )

def join_query_2():
    return Query \
        .from_(categories) \
        .left_join(books) \
        .on(categories.id == books.category_id) \
        .select(
            categories.name,
            fn.Count(books.id).as_('book_count')
        ) \
        .groupby(categories.name)

# 3 запроса с агрегацией
def aggregate_query_1():
    return Query \
        .from_(books) \
        .select(
            fn.Avg(books.price).as_('avg_price')
        )

def aggregate_query_2():
    return Query \
        .from_(books) \
        .select(
            books.category_id,
            fn.Max(books.price).as_('max_price')
        ) \
        .groupby(books.category_id)

def aggregate_query_3():
    return Query \
        .from_(categories) \
        .join(books) \
        .on(categories.id == books.category_id) \
        .select(
            categories.name,
            fn.Sum(books.price).as_('total_value')
        ) \
        .groupby(categories.name)

# Выполнение запросов
def execute_queries():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    queries = [
        ("JOIN 1", join_query_1()),
        ("JOIN 2", join_query_2()),
        ("Aggregate 1", aggregate_query_1()),
        ("Aggregate 2", aggregate_query_2()),
        ("Aggregate 3", aggregate_query_3())
    ]
    
    for name, query in queries:
        print(f"\n{name}: {query.get_sql()}")
        cursor.execute(query.get_sql())
        print(cursor.fetchall())
    
    conn.close()

if __name__ == "__main__":
    execute_queries()