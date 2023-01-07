'''
Функция проверяет, есть ли объява в БД, если нет, а) присылает её в телегу б) добавляет в БД в)делает принты
'''


def check_database(card: str) -> None:
    title: str = card.find('h6').text
    with sqlite3.connect('DB/realty4.db') as connection:
        cursor = connection.cursor()
        cursor.execute('''
            SELECT title FROM offers WHERE title = (?)
        ''', (title,))
        result = cursor.fetchone()
        if result is None:
            offer = get_offer(card)
            send_telegram(offer)
            cursor.execute('''
                INSERT INTO offers
                VALUES(NULL, :title, :price, :district, :time, :lnk)
            ''', offer)
            connection.commit()
            print(f'●Объявление ---{title}--- добавлено в базу данных')
            print(f'Время добавления в базу данных: {time.ctime(time.time())}')
            print(f'Время с начала запуска скрипта: {time.time() - start_time}')