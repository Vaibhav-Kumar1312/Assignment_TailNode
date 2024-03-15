import mysql.connector
from mysql.connector import errorcode
import requests
from bs4 import BeautifulSoup

try:
  db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='password'
)
except mysql.connector.Error as err:
    print(err)

# Create a cursor object to execute SQL queries
cursor = db.cursor()


# Creating Database
def create_database(cursor):
    try:
        cursor.execute("CREATE DATABASE scraped_Book_Data")
    except mysql.connector.Error as err:
        print("Failed creating database: scraped_Book_Data")
        exit(1)

try:
    cursor.execute("USE scraped_Book_Data")
except mysql.connector.Error as err:
    print("Database scraped_Book_Data does not exists.")
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        print("Database scraped_Book_Data created successfully.")
        db.database = "scraped_Book_Data"
    else:
        print(err)
        exit(1)


# Create a table to store books data if not exists
create_books_table_query = """
CREATE TABLE IF NOT EXISTS books_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    price VARCHAR(255),
    availability VARCHAR(50),
    rating VARCHAR(10)
)
"""
cursor.execute(create_books_table_query)

# Scrape and store books data from all 50 pages
base_url = "http://books.toscrape.com/catalogue/page-{}.html"
for page_num in range(1, 51):
    page_url = base_url.format(page_num)
    # scrape_and_store_books_data(page_url)
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    books = soup.find_all('article', class_='product_pod')
    print("okay-----",books[0].find('p', class_='price_color').get_text())

    for book in books:
        title = book.h3.a['title']
        price = book.find('p', class_='price_color').get_text()
        availability = book.find('p', class_='instock availability').get_text().strip()
        rating = book.find('p', class_='star-rating')['class'][1]

        # Insert book data into the database
        insert_book_query = """
        INSERT INTO books_data (title, price, availability, rating) 
        VALUES (%s, %s, %s, %s)
        """
        book_data = (title, price, availability, rating)
        cursor.execute(insert_book_query, book_data)

    # Commit the transaction
    db.commit()

# Close the cursor and connection
cursor.close()
db.close()
