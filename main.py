import sqlite3
import sys

with sqlite3.connect('venv/database.db') as db:
    cursor = db.cursor()
    query = """  CREATE TABLE IF NOT EXISTS expenses(Name TEXT, Balance INTEGER, Currency TEXT, Blocked INTEGER)  """
    cursor.execute(query)

def print_message():
    message = int(input('''Напишите пожалуйста какую информатцию вы хотите посмотреть: 
                                1. Узнать баланс
                                2. Пополнить кошелёк
                                3. Снять деньги с кошелька
                                4. Перевести деньги на другой кошелёк
                                5. Заблокировать/Разблокировать карту
                                6. Посмотреть историю операции
                                7. Выйти из кошелька
                                '''))
    operations = [balance_print, set_money, get_money, transfer_money, blocked_or_unblocked_account, exit_account]
    output = operations[message - 1]()
    print(output)

def add_to_database(name_x, balance_x, currency_x, check_block_x):
    try:
        cursor.execute("""  INSERT INTO expenses(name, balance, currency, blocked) VALUES('%s', '%s', '%s', '%s') """ % (
            name_x, balance_x, currency_x, check_block_x))
        print('Новый пользователь успешно добавлен')
        db.commit()
        print_message()
    except sqlite3.Error as error:
        print('Ошибка при работе с SQLite', error)

def check_blocked_account():
    info = cursor.execute(""" SELECT blocked FROM expenses WHERE name = '%s' """ % (owner_name))
    x = info.fetchall()
    if bool(x[0][0]) == 0:
        return True
    else:
        return False

def balance_print():
    info = cursor.execute('SELECT * FROM expenses WHERE name=?', (owner_name,))
    result = info.fetchall()
    for row in result:
        print(f'Имя: {row[0]}')
        print(f'Ваш баланс состовляет: {row[1]}')
        print(f'Валюта: {row[2]}')
    print_message()

def set_money():
    try:
        if check_blocked_account():
            sqlite_connection = sqlite3.connect('venv/database.db')
            cursor = sqlite_connection.cursor()
            x = int(input('Введите сумму которую вы хотите внести: '))
            cursor.execute(""" Update expenses set balance = balance + '%s' where name = '%s' """ % (x, owner_name))
            sqlite_connection.commit()
            print('Пополнение кошелька прошла успешно!')
            cursor.close()
            print_message()
        else:
            print('''Ваш аккаунт заблокирован!''')
            print_message()
    except sqlite3.Error as error:
        print('Ошибка при работе с SQLite', error)

def get_money():
    try:
        if check_blocked_account():
            sqlite_connection = sqlite3.connect('venv/database.db')
            cursor = sqlite_connection.cursor()
            x = int(input('Введите сумму которую вы хотите снять: '))
            info = cursor.execute(""" SELECT balance FROM expenses WHERE name='%s' """ % (owner_name))
            y = info.fetchone()
            sqlite_connection.commit()
            if x < y[0]:
                cursor.execute(""" Update expenses set balance = balance - '%s' where name = '%s' """ % (x, owner_name))
                sqlite_connection.commit()
                print('Выдача наличных прошла успешно!')
            else:
                print('Недостаточно средств на счёте!')
            cursor.close()
            print_message()
        else:
            print('''Ваш аккаунт заблокирован!''')
            print_message()
    except sqlite3.Error as error:
        print('Ошибка при работе с SQLite', error)

def transfer_money():
    try:
        if check_blocked_account():
            sqlite_connection = sqlite3.connect('venv/database.db')
            cursor = sqlite_connection.cursor()
            x = int(input('Введите сумму которую вы хотите перевести: '))
            user_to = input('Введите имя пользователя, которому нужно перевести деньги: ')
            info = cursor.execute(""" SELECT balance FROM expenses WHERE name='%s' """ % (owner_name))
            info_user_out = info.fetchone()

            info_user_to = cursor.execute(""" SELECT * FROM expenses WHERE name='%s' """ % (user_to))

            if info_user_to:
                print('Проверьте правильность введёного имени! Мы не смогли найти данного пользователя в базе данных.')
            elif (x < info_user_out[0]):
                cursor.execute(""" Update expenses set balance = balance + '%s' where name = '%s' """ % (x, user_to))
                cursor.execute(""" Update expenses set balance = balance - '%s' where name = '%s' """ % (x, owner_name))
                sqlite_connection.commit()
                print('Перевод денег на другой счёт прошёл успешно!')
            else:
                print('Недостаточно средств на счёте!')
            cursor.close()
            print_message()
        else:
            print('Ваш аккаунт заблокирован!')
            print_message()
    except sqlite3.Error as error:
        print('Ошибка при работе с SQLite', error)

def blocked_or_unblocked_account():
    if not check_blocked_account():
        x = str(input('Вы хотите разблокировать свой счёт? '))
        if x in ['Yes', 'Да','yes','да']:
            cursor.execute(""" Update expenses set blocked = '%s' where name = '%s' """ % (0, owner_name))
            print_message()
    else:
        x = str(input('Вы действительно хотите заблокировать свой счёт? '))
        if x in ['Yes', 'Да','yes','да']:
            cursor.execute(""" Update expenses set blocked = '%s' where name = '%s' """ % (0, owner_name))
            print_message()

def exit_account():
    sys.exit(0)

owner_name = input('''Здравствуйте,
Введите пожалуйста ваше имя: 
''')

info = cursor.execute('SELECT * FROM expenses WHERE name=?', (owner_name,))
if info.fetchone() is None:
    # Делаем когда нету человека в бд
    currency = input('Введите пожалуйста в какой валюте хранить ваши сбережения: ')
    add_to_database(owner_name, 0, currency, 0)
else:
    # Делаем когда есть человек в бд
    print_message()
