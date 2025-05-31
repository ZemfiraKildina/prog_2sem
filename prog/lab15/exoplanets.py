import sqlite3
import requests
from bs4 import BeautifulSoup
import re

# ----------------------------
# ШАГ 1: Парсинг данных с Википедии
# ----------------------------

def parse_wikipedia_data():
    url = "https://ru.wikipedia.org/wiki/Список_кратных_планетных_систем"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    table = soup.find('table', {'class': 'wikitable'})
    data = []
    
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        if len(cols) < 7:
            continue
        
        star_name = cols[0].get_text(strip=True)
        constellation = cols[1].get_text(strip=True)
        
        # Обработка расстояния
        # Обработка расстояния (с обработкой ошибок)
        distance = None
        try:
            distance_str = re.sub(r'[^\d.]', '', cols[2].get_text(strip=True).replace(',', '.'))
            if distance_str:
                distance = float(distance_str)
        except (ValueError, TypeError):
            distance = None
        
        # Обработка спектрального класса
        spectral_class = cols[3].get_text(strip=True).split()[0]
        
        # Обработка количества планет (исправление)
        planets_text = cols[-1].get_text(strip=True)
        # Извлекаем первое число из текста (игнорируем примечания в скобках)
        planets_match = re.search(r'\d+', planets_text)
        planets = int(planets_match.group()) if planets_match else 0
        
        data.append({
            'star': star_name,
            'constellation': constellation,
            'distance': distance,
            'spectral_class': spectral_class,
            'planets': planets
        })
    
    return data

# ----------------------------
# ШАГ 2: Создание БД и таблиц
# ----------------------------

def create_database_schema(db_name='exoplanets.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Создаем таблицу созвездий
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS constellations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    ''')
    
    # Создаем таблицу спектральных классов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS spectral_classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class TEXT UNIQUE NOT NULL
    )
    ''')
    
    # Создаем таблицу звезд
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        constellation_id INTEGER NOT NULL,
        spectral_class_id INTEGER NOT NULL,
        distance REAL,
        planets_count INTEGER NOT NULL,
        FOREIGN KEY (constellation_id) REFERENCES constellations(id),
        FOREIGN KEY (spectral_class_id) REFERENCES spectral_classes(id)
    )
    ''')
    
    conn.commit()
    return conn

# ----------------------------
# ШАГ 3: Заполнение БД данными
# ----------------------------

def populate_database(conn, data):
    cursor = conn.cursor()
    
    # Собираем уникальные значения
    constellations = {item['constellation'] for item in data}
    spectral_classes = {item['spectral_class'] for item in data}
    
    # Заполняем созвездия
    constellation_ids = {}
    for name in constellations:
        cursor.execute('INSERT OR IGNORE INTO constellations (name) VALUES (?)', (name,))
        cursor.execute('SELECT id FROM constellations WHERE name = ?', (name,))
        constellation_ids[name] = cursor.fetchone()[0]
    
    # Заполняем спектральные классы
    spectral_class_ids = {}
    for class_name in spectral_classes:
        cursor.execute('INSERT OR IGNORE INTO spectral_classes (class) VALUES (?)', (class_name,))
        cursor.execute('SELECT id FROM spectral_classes WHERE class = ?', (class_name,))
        spectral_class_ids[class_name] = cursor.fetchone()[0]
    
    # Заполняем звезды
    for item in data:
        cursor.execute('''
        INSERT INTO stars (name, constellation_id, spectral_class_id, distance, planets_count)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            item['star'],
            constellation_ids[item['constellation']],
            spectral_class_ids[item['spectral_class']],
            item['distance'],
            item['planets']
        ))
    
    conn.commit()

# ----------------------------
# ШАГ 4: SQL-запросы к базе данных
# ----------------------------

def execute_queries(conn, n=5):
    cursor = conn.cursor()
    
    print(f"\nТоп-{n} ближайших систем:")
    cursor.execute('''
    SELECT s.name, c.name, s.distance 
    FROM stars s
    JOIN constellations c ON s.constellation_id = c.id
    WHERE s.distance IS NOT NULL
    ORDER BY s.distance ASC
    LIMIT ?
    ''', (n,))
    for row in cursor.fetchall():
        print(f"{row[0]} ({row[1]}): {row[2]} св. лет")

    print(f"\nТоп-{n} самых далеких систем:")
    cursor.execute('''
    SELECT s.name, c.name, s.distance 
    FROM stars s
    JOIN constellations c ON s.constellation_id = c.id
    WHERE s.distance IS NOT NULL
    ORDER BY s.distance DESC
    LIMIT ?
    ''', (n,))
    for row in cursor.fetchall():
        print(f"{row[0]} ({row[1]}): {row[2]} св. лет")

    print(f"\nТоп-{n} систем по количеству планет:")
    cursor.execute('''
    SELECT s.name, c.name, s.planets_count 
    FROM stars s
    JOIN constellations c ON s.constellation_id = c.id
    ORDER BY s.planets_count DESC
    LIMIT ?
    ''', (n,))
    for row in cursor.fetchall():
        print(f"{row[0]} ({row[1]}): {row[2]} планет")

    print("\nСамые богатые системы по созвездиям:")
    cursor.execute('''
    SELECT 
        c.name AS constellation,
        s.name AS star,
        MAX(s.planets_count) AS max_planets
    FROM stars s
    JOIN constellations c ON s.constellation_id = c.id
    GROUP BY c.id
    ''')
    for row in cursor.fetchall():
        print(f"{row[0]}: {row[1]} ({row[2]} планет)")

# ----------------------------
# Главная функция
# ----------------------------

def main():
    # Парсим данные
    print("Парсинг данных с Википедии...")
    data = parse_wikipedia_data()
    
    # Создаем БД
    print("Создание базы данных...")
    conn = create_database_schema()
    
    # Заполняем БД
    print("Заполнение базы данных...")
    populate_database(conn, data)
    
    # Выполняем запросы
    print("Выполнение запросов...")
    execute_queries(conn)
    
    # Закрываем соединение
    conn.close()
    print("\nГотово! База данных сохранена в файле 'exoplanets.db'")

if __name__ == "__main__":
    main()