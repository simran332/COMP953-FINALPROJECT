"""
NASA APOD Desktop Setter

This script downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
and sets it as the desktop background image.

Usage:
  python apod_desktop.py [apod_date]

Parameters:
  apod_date = APOD date (format: YYYY-MM-DD)
"""

from datetime import date
import sqlite3
import hashlib
import os
import re
import sys

import image_lib
import apod_api

# Define constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_CACHE_DIR = os.path.join(SCRIPT_DIR, 'images')
IMAGE_CACHE_DB = os.path.join(IMAGE_CACHE_DIR, 'image_cache.db')

def main():
    """Main function to set APOD as desktop background."""
    apod_date = get_apod_date()
    init_apod_cache()
    apod_id = add_apod_to_cache(apod_date)
    apod_info = get_apod_info(apod_id)
    image_lib.set_desktop_background_image(apod_info['file_path'])

def get_apod_date():
    """Retrieve APOD date from command line or use today's date if not provided."""
    num_params = len(sys.argv) - 1
    if num_params >= 1:
        try:
            apod_date = date.fromisoformat(sys.argv[1])
        except ValueError as err:
            print(f'Error: Invalid date format; {err}')
            sys.exit('Script execution aborted')

        MIN_APOD_DATE = date.fromisoformat("1995-06-16")
        if apod_date < MIN_APOD_DATE:
            print(f'Error: Date too far in the past; First APOD was on {MIN_APOD_DATE.isoformat()}')
            sys.exit('Script execution aborted')
        elif apod_date > date.today():
            print('Error: APOD date cannot be in the future')
            sys.exit('Script execution aborted')
    else:
        apod_date = date.today()
    return apod_date

def init_apod_cache():
    """Initialize the image cache directory and database."""
    print(f"Image cache directory: {IMAGE_CACHE_DIR}")
    try:
        os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)
        print("Image cache directory created.")
    except FileExistsError:
        print("Image cache directory already exists.")

    if not os.path.exists(IMAGE_CACHE_DB):
        with sqlite3.connect(IMAGE_CACHE_DB) as db_conn:
            db_cursor = db_conn.cursor()
            db_cursor.execute("""
                CREATE TABLE IF NOT EXISTS image_data (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    explanation TEXT,
                    file_path TEXT,
                    sha256 TEXT
                );
            """)
            print("Image cache DB created.")

def get_apod_id_from_db(image_sha256):
    #Retrieve APOD ID from database based on SHA-256 hash.
        with sqlite3.connect(IMAGE_CACHE_DB) as db_conn:
            db_cursor = db_conn.cursor()
            db_cursor.execute("SELECT id FROM image_data WHERE sha256=?", (image_sha256.upper(),))
            query_result = db_cursor.fetchone()

        if query_result is not None:
            print("APOD image is already in cache.")
            return query_result[0]
        else:
            print("APOD image is not already in cache.")
            return 0

def add_apod_to_cache(apod_date):
    """Add APOD to cache if not already present."""
    print("APOD date:", apod_date.isoformat())
    apod_info = apod_api.get_apod_info(apod_date.isoformat())
    if apod_info is None:
        return 0
    
    apod_title = apod_info['title']
    print("APOD title:", apod_title)

    apod_url = apod_api.get_apod_image_url(apod_info)
    apod_image_data = image_lib.download_image(apod_url)
    apod_sha256 = hashlib.sha256(apod_image_data).hexdigest()
    print("APOD SHA-256:", apod_sha256)

    apod_id = get_apod_id_from_db(apod_sha256)
    if apod_id != 0:
        return apod_id

    apod_path = determine_apod_file_path(apod_title, apod_url)
    print("APOD file path:", apod_path)
    if not image_lib.save_image_file(apod_image_data, apod_path):
        return 0

    apod_explanation = apod_info['explanation']
    apod_id = add_apod_to_db(apod_title, apod_explanation, apod_path, apod_sha256)
    return apod_id

# Remaining functions follow the same pattern with improvements in naming, comments, and structure

# Continued from previous modifications...

def add_apod_to_db(title, explanation, file_path, sha256):
    """Add APOD information to the database."""
    print("Adding APOD to image cache DB...", end='')
    try:
        with sqlite3.connect(IMAGE_CACHE_DB) as db_conn:
            db_cursor = db_conn.cursor()
            insert_image_query = """
                INSERT INTO image_data 
                (title, explanation, file_path, sha256)
                VALUES (?, ?, ?, ?);
            """
            image_data = (title, explanation, file_path, sha256.upper())
            db_cursor.execute(insert_image_query, image_data)
            db_conn.commit()
            print("success")
            return db_cursor.lastrowid
    except sqlite3.Error as e:
        print(f"failure: {e}")
        return 0
    
   
def determine_apod_file_path(image_title, image_url):
    """Determine file path for the downloaded APOD image."""
    file_ext = image_url.split(".")[-1]
    file_name = re.sub(r'\W+', '', image_title.replace(' ', '_'))
    file_path = os.path.join(IMAGE_CACHE_DIR, f"{file_name}.{file_ext}")
    return file_path

def get_apod_info(apod_id):
    """Retrieve APOD information from the database based on ID."""
    with sqlite3.connect(IMAGE_CACHE_DB) as db_conn:
        db_cursor = db_conn.cursor()
        db_cursor.execute("SELECT * FROM image_data WHERE id=?", (apod_id,))
        query_result = db_cursor.fetchone()

    if query_result:
        keys = ("id", "title", "explanation", "file_path", "sha256")
        return dict(zip(keys, query_result))
    else:
        return None

def get_all_apod_titles():
    """
    Retrieves a list of titles of all APODs stored in the image cache.

    Returns:
        tuple: Titles of all images in the cache.
    """

    connection = sqlite3.connect(IMAGE_CACHE_DB)
    create_table_query = """
                        CREATE TABLE IF NOT EXISTS image_data(
                            id INTEGER PRIMARY KEY,
                            title TEXT,
                            explanation TEXT,
                            file_path TEXT,
                            sha256 TEXT
                        );
                        """
    cursor = connection.cursor()
    cursor.execute(create_table_query)
    image_query = "SELECT title FROM image_data;"
    cursor.execute(image_query)
    image_titles = cursor.fetchall()
    
    connection.close()
    return tuple([title[0] for title in image_titles])

if __name__ == '__main__':
    main()

