import sqlite3
import time

start_time = time.time()

class Database:

    def __init__(self, db_path):
        self.db_path = db_path

    # TODO: make Database funcs async

    def user_is_in_db(self, user_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # cursor.execute(f'SELECT user_id FROM offers WHERE user_id={user_id}')
            cursor.execute(f'SELECT EXISTS(SELECT user_id FROM offers WHERE user_id={user_id})')
            result = cursor.fetchone()
            print(result)
            return result == 0

    def ad_is_in_db(self, card: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            title = card.find('h6').text
            # cursor.execute('''
            #         SELECT title FROM offers WHERE title = (?)
            #     ''', (title,))
            cursor.execute('''
                    SELECT count(*) FROM offers WHERE title = (?)
                ''', (title,))
            result = cursor.fetchone()
            print(result)
            return result == 0

    def send_to_db(self, offer: dict):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                            INSERT INTO offers
                            VALUES(NULL, :user_id, :название, :цена, :район, :время_публикации, :ссылка, :search_link, 
                            :параметры_поиска)
                        ''', offer)
            conn.commit()
            print(f'●Объявление ---{offer["название"]}--- добавлено в базу данных')
            print(f'Время добавления в базу данных: {time.ctime(time.time())}')
            print(f'Время с начала запуска скрипта: {time.time() - start_time}')

    def fetch(self, column: str, user_id: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''SELECT {column} FROM offers WHERE (ad_id = (SELECT MAX(ad_id) FROM offers) and
            user_id = (?))''', (user_id,))
            return cursor.fetchone()

    def del_db_content(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''DELETE FROM offers''')


