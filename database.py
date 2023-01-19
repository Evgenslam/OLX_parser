class Database:

    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    # Here I tried to implement context manager, but failed
    # def __init__(self, db_path: str):
    #     self.db_path = open(db_path)

    # def __init__(self, file_name, method):
    #     self.file_obj = open(file_name, method)

    # def __enter__(self):
    #     return self.db_path
    #
    # def __exit__(self, type, value, traceback):
    #     self.db_path.close()

    def check_entry(self, card: str):
        title = card.find('h6').text
        self.cursor.execute('''
                SELECT title FROM offers WHERE title = (?)
            ''', (title,))
        result = self.cursor.fetchone()
        return result

    def send_to_db(self, offer: str):
        self.cursor.execute('''
                        INSERT INTO offers
                        VALUES(NULL, :title, :price, :district, :time, :lnk)
                    ''', offer)
        self.conn.commit()
        print(f'●Объявление ---{offer["title"]}--- добавлено в базу данных')
        print(f'Время добавления в базу данных: {time.ctime(time.time())}')
        print(f'Время с начала запуска скрипта: {time.time() - start_time}')

    def close(self):
        self.conn.close()