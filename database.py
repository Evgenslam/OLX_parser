import sqlite3
import time

start_time = time.time()

class Database:

    def __init__(self, db_path):
        self.db_path = db_path

    # TODO: add create_db function
    # TODO: add verification function
    # TODO: make Database funcs async

    #def create_db():

    def verification(self, user_id):
        response = self.db_path.fetchrow(f'SELECT EXISTS(SELECT user_id FROM offers WHERE user_id={user_id})')
        return True if response else False

    def is_in_db(self, card: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            title = card.find('h6').text
            cursor.execute('''
                    SELECT title FROM offers WHERE title = (?)
                ''', (title,))
            result = cursor.fetchone()
            return result

    def send_to_db(self, offer: dict):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                            INSERT INTO offers
                            VALUES(NULL, :user_id, :title, :price, :district, :time, :lnk)
                        ''', offer)
            conn.commit()
            print(f'●Объявление ---{offer["title"]}--- добавлено в базу данных')
            print(f'Время добавления в базу данных: {time.ctime(time.time())}')
            print(f'Время с начала запуска скрипта: {time.time() - start_time}')

    def del_db_content(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''DELETE FROM offers''')


