import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT", 3306))
    )

def create_table():
    conn=get_connection()
    cursor=conn.cursor()
    query="""
        Create table if not exists properties(
        id int auto_increment primary key,
        title text,
        price varchar(100),
        location varchar(200),
        area varchar(100),
        beds varchar(20),
        baths varchar(20),
        city varchar(50),
        property_type varchar(50),
        listing_date varchar(100),
        page_url text,
        phone Varchar(20),
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        sentiment_label VARCHAR(20))"""
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
    print("Table Ready")
