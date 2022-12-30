import sqlite3

def main():
    with sqlite3.connect('realty4.db') as connection:
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS offers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                price TEXT, 
                district TEXT,
                time TEXT,
                lnk TEXT 
                ) ''')

if __name__ == "__main__":
    main()
