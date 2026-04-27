import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    conn=mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME"),
        auth_plugin="mysql_native_password"
    )
    return conn

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
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
    print("Table Ready")
