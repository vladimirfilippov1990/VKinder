import psycopg2
from cfg import postgresql

with psycopg2.connect(postgresql) as conn:
    def create_table() -> None:
        """ Функция, которая сначала удаляет таблицу 'Partners', если она уже есть, а затем создает новую. """
        
        with conn.cursor() as cursor:
            cursor.execute("""DROP TABLE IF EXISTS Partners;""")
            conn.commit()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Partners(
                    finder_id INTEGER,
                    partner_id INTEGER,
                    first_name VARCHAR(40) NOT NULL,
                    last_name VARCHAR(40) NOT NULL,
                    PRIMARY KEY(finder_id, partner_id)
                    );
                """)
            conn.commit() 
        conn.close()


    def insert_partners(data):
        """ Функция, добавляющая в таблицу 'Partner' всех(!!!) подошедших по заданным критериям кандидатов. """
        
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Partners(finder_id, partner_id, first_name, last_name) VALUES(%s, %s, %s, %s);
                """, (data[0], data[1], data[2], data[3]))
            conn.commit()
        


    def get_user_from_db(finder_id):
        """ Функция, выдающая по запросу пользователя данные об одном случайном кандидате из таблицы 'Partners'. """

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT partner_id, first_name, last_name FROM Partners WHERE finder_id = %s;
                """, (finder_id, ))
            return cursor.fetchone()
        


    def delete_candidate(finder_id, partner_id):
        """ Функция, которая удаляет просмотренных кандидатов из таблицы, чтобы они больше не выпадали при запросе. """

        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM Partners WHERE partner_id = %s AND finder_id = %s;
                """, (partner_id, finder_id,))
            conn.commit()
        

    def delete_candidates(finder_id):
        """ Функция, которая удаляет просмотренных кандидатов из таблицы, чтобы они больше не выпадали при запросе. """

        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM Partners WHERE finder_id = %s;
                """, (finder_id,))
            conn.commit()


    def create_table_user():
        """ Функция, которая создает таблицу 'Users', если её нет. """

        with conn.cursor() as cursor:
            cursor.execute("""DROP TABLE IF EXISTS Users;""")
            conn.commit()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Users (
                    id INTEGER PRIMARY KEY,
                    fcity INTEGER,
                    fgender INTEGER CHECK(fgender IN(1, 2)),  
                    fage INTEGER,
                    ffamily INTEGER CHECK(ffamily IN(1, 2, 3, 4, 5, 6, 7, 8)),
                    step INTEGER CHECK (step IN(1, 2, 3, 4, 5, 6))
                );
                """)
            conn.commit()


    def insert_user(uid):
        """ Функция, добавляющая в таблицу 'Users' нового пользователя и указывающая ему 1 шаг использованич бота """
        
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Users(id, step) VALUES(%s, 1);
                """, (uid, ))
            conn.commit()
    

    def update_user_city(uid, cid):
        """ Функция, добавляющая в таблицу 'Users' нового пользователя и указывающая ему 1 шаг использованич бота """
        
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE Users SET fcity = %s WHERE id = %s;
                """, (cid, uid, ))
            conn.commit()

        
    def update_user_age(uid, age):
        """ Функция, добавляющая в таблицу 'Users' нового пользователя и указывающая ему 1 шаг использованич бота """
        
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE Users SET fage = %s WHERE id = %s;
                """, (age, uid, ))
            conn.commit()


    def update_user_gender(uid, gender):
        """ Функция, добавляющая в таблицу 'Users' нового пользователя и указывающая ему 1 шаг использованич бота """
        
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE Users SET fgender = %s WHERE id = %s;
                """, (gender, uid, ))
            conn.commit()


    def update_user_family(uid, family):
        """ Функция, добавляющая в таблицу 'Users' нового пользователя и указывающая ему 1 шаг использованич бота """
        
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE Users SET ffamily = %s WHERE id = %s;
                """, (family, uid, ))
            conn.commit()


    def update_user_position(uid, step):
        """ Функция, добавляющая в таблицу 'Users' нового пользователя и указывающая ему 1 шаг использованич бота """
        
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE Users SET step = %s WHERE id = %s;
                """, (step, uid, ))
            conn.commit()


    def get_user_settings(uid):
        """ Функция, добавляющая в таблицу 'Users' нового пользователя и указывающая ему 1 шаг использованич бота """ 
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT fcity, fgender, fage, ffamily FROM Users WHERE id = %s;
                """, (uid, ))
            
            return cursor.fetchone()
        
    def take_position(uid):
        """ Функция, выдающая по запросу пользователя данные об одном случайном кандидате из таблицы 'Partners'. """
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT step FROM Users WHERE id = %s;
                """, (uid, ))
            position = cursor.fetchone()
            if position:
                return position[0]
            else:
                insert_user(uid)
                return 1
                