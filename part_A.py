import mysql.connector
from mysql.connector import errorcode
import requests

# Connect to MySQL server
try:
  db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='password'
)
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
    

# Create a cursor object to execute SQL queries
mycursor = db.cursor()

# Creating Database
def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE user_and_post_DB")
    except mysql.connector.Error as err:
        print("Failed creating database: user_and_post_DB")
        exit(1)

try:
    mycursor.execute("USE user_and_post_DB")
except mysql.connector.Error as err:
    print("Database user_and_post_DB does not exists.")
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(mycursor)
        print("Database user_and_post_DB created successfully.")
        db.database = "user_and_post_DB"
    else:
        print(err)
        exit(1)

# Create users table if not exists
try:
    # mycursor.execute(create_users_table_query)
    mycursor.execute("CREATE TABLE IF NOT EXISTS users(id VARCHAR(50) PRIMARY KEY,title VARCHAR(255),firstName VARCHAR(255),lastName VARCHAR(255),picture VARCHAR(255))")
except mysql.connector.Error as err:
    print(err)


app_id = "65f3ddc155b612519a5f163a"
users_api_url = "https://dummyapi.io/data/v1/user"
headers = {"app-id":app_id}
response = requests.get(users_api_url,headers=headers)
usersData = response.json()['data']

# Insert users data into the database
insert_user_query = """
INSERT INTO users (id, title, firstName, lastName, picture) 
VALUES (%s, %s, %s, %s, %s)
"""
for user in usersData:
    user_tuple = (user["id"], user["title"], user["firstName"], user["lastName"], user["picture"])
    mycursor.execute(insert_user_query, user_tuple)

# Commit the transaction
db.commit()

# Create posts table if not exists
try:
    mycursor.execute("CREATE TABLE IF NOT EXISTS posts(id VARCHAR(50) PRIMARY KEY,userId VARCHAR(50),image VARCHAR(255),likes INTEGER,text VARCHAR(255),publishDate VARCHAR(255),FOREIGN KEY (userId) REFERENCES users(id))")
except mysql.connector.Error as err:
    print(err)


# Fetch users list from the database
mycursor.execute("SELECT id FROM users")
user_ids = mycursor.fetchall()

# Fetch corresponding posts data using user IDs and store it in the database
for user_id in user_ids:
    user_id = user_id[0]
    posts_api_url = f"https://dummyapi.io/data/v1/user/{user_id}/post"
    response = requests.get(posts_api_url, headers=headers)
    posts_data = response.json()["data"]
    
    # Insert posts data into the database
    insert_post_query = """
    INSERT INTO posts (id, userId, image, likes, text, publishDate) 
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    for post in posts_data:
        post_tuple = (post["id"], post['owner']['id'], post["image"], post["likes"], post["text"],post['publishDate'],)
        mycursor.execute(insert_post_query, post_tuple)

# Commit the transaction
db.commit()

# Close the cursor and connection
mycursor.close()
db.close()
