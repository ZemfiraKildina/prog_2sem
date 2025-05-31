from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sqlite3
from database import create_tables, insert_data

# Настройка браузера
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Фоновый режим
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver

# Парсинг данных с сайта
def parse_data(driver):
    driver.get("https://books.toscrape.com/")
    books_data = []
    categories_data = []

    # Парсинг категорий
    category_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".nav-list li a"))
    )
    for idx, cat in enumerate(category_elements[:5], 1):  # Берем 5 категорий
        categories_data.append({
            'id': idx,
            'name': cat.text.strip(),
            'url': cat.get_attribute('href')
        })

    # Парсинг книг
    book_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.product_pod"))
    )
    for idx, book in enumerate(book_elements[:10], 1):  # Берем 10 книг
        title = book.find_element(By.CSS_SELECTOR, "h3 a").get_attribute('title')
        price = float(book.find_element(By.CSS_SELECTOR, ".price_color").text[1:])
        category_id = (idx % len(categories_data)) + 1  # Распределение по категориям
        
        books_data.append({
            'id': idx,
            'title': title,
            'price': price,
            'category_id': category_id
        })
    
    return books_data, categories_data

def main():
    driver = setup_driver()
    try:
        books, categories = parse_data(driver)
        conn = sqlite3.connect('library.db')
        create_tables(conn)
        insert_data(conn, books, categories)
        print("Данные успешно сохранены в БД")
    finally:
        driver.quit()
        conn.close()

if __name__ == "__main__":
    main()