import psycopg2


def create_db(conn):
    with conn.cursor() as cur:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users(
                id SERIAL PRIMARY KEY,
                name VARCHAR(128) NOT NULL,
                last_name VARCHAR(128) NOT NULL,
                email VARCHAR(256) UNIQUE
            );
            ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS phone(
                id INTEGER REFERENCES users(id),
                phone VARCHAR(32) NOT NULL UNIQUE
            );
            ''')


def add_client(conn, name, last_name, email, phones=[]):
     with conn.cursor() as cur:
        cur.execute('''
            INSERT INTO users(name, last_name, email) VALUES (%s, %s, %s) RETURNING id
            ''', (name, last_name, email))
        
        id = cur.fetchone()[0]

        for phone in phones:
            add_phone(conn, id, phone)


def add_phone(conn, id, phone):
    with conn.cursor() as cur:
        cur.execute('''
            INSERT INTO phone(id, phone) VALUES (%s, %s)
            ''', (id, phone))


def change_client(conn, id, **kwargs):
    args = []
    query = '''UPDATE users SET '''
    
    for arg in kwargs.items():
        if arg[0] == 'phones':
            with conn.cursor() as cur:
                cur.execute('''
                    DELETE FROM phone WHERE id = %s
                    ''', (id,))
                for phone in arg[1]:
                    add_phone(conn, id, phone)
        else:
            args.append(arg[1])
            if len(args) > 1:
                query = query + ' AND '
            query = query + arg[0] + ' = %s'


    query = query + ' WHERE id= %s'
    args.append(id)

    with conn.cursor() as cur:
        cur.execute(query, (args))
        
    print(f'Изменены данные пользователя с ID {id}, измененные данные {kwargs}')


def delete_phone(conn, id, phone):
    with conn.cursor() as cur:
        cur.execute('''
            DELETE FROM phone WHERE id = %s and phone = %s RETURNING id, phone
            ''', (id, phone))
        delete_info = cur.fetchone()

    print(f'Удален номер телефона {delete_info[1]}, принадлежащий пользователю с ID {delete_info[0]}')


def delete_client(conn, id):
    with conn.cursor() as cur:
        cur.execute('''
            DELETE FROM phone WHERE id = %s
            ''', (id,))
        cur.execute('''
            DELETE FROM users WHERE id = %s
            ''', (id,))
    
    print(f'Удален пользователь с ID {id}')


def find_client(conn, **kwargs):
    args = []
    query = '''SELECT * FROM users WHERE '''
    
    for arg in kwargs.items():
        args.append(arg[1])
        if len(args) > 1:
            query = query + ' AND '
        query = query + arg[0] + '= %s'
    
    with conn.cursor() as cur:
        cur.execute(query, (args))
        result = cur.fetchone()

    print(f'Найден пользователь {result[1]} {result[2]}, его ID {result[0]}')


with psycopg2.connect(database="test", user="postgres") as conn:
    create_db(conn)
    add_client(conn, 'Игорь', 'Важенин', 'knowall45@ya.ru', phones=['+79125232100', '+79125722100'])
    add_client(conn, 'Igor', 'Vazhenin', 'vidok0577@gmail.com', phones=['+79991234567'])
    add_client(conn, 'Петр', 'Иванов', '123@gmail.com', phones=['+79226722100'])
    add_client(conn, 'Иван', 'Петров', '456@gmail.com')
    add_phone(conn, '4', '+79991234567_')
    add_phone(conn, '3', '+79997654321')
    delete_phone(conn, '3', '+79997654321')
    delete_client(conn, '2')
    change_client(conn, '1', name='Илья', phones=['675765875', '765674653', '87643654'])
    change_client(conn, '2', name='Игорь')
    find_client(conn, email='knowall45@ya.ru')
conn.close()