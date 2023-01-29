import sqlite3
import time

start_time = time.time()

class Database:

    def __init__(self, db_path):
        self.db_path = db_path

    def check_entry(self, card: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            title = card.find('h6').text
            cursor.execute('''
                    SELECT title FROM offers WHERE title = (?)
                ''', (title,))
            result = cursor.fetchone()
            return result

    def send_to_db(self, offer: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                            INSERT INTO offers
                            VALUES(NULL, :title, :price, :district, :time, :lnk)
                        ''', offer)
            conn.commit()
            print(f'●Объявление ---{offer["title"]}--- добавлено в базу данных')
            print(f'Время добавления в базу данных: {time.ctime(time.time())}')
            print(f'Время с начала запуска скрипта: {time.time() - start_time}')

    def del_db_content(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''DELETE FROM offers''')



# db = Database(db_path='DB/realty4.db')
# db.del_db_content()