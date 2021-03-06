import datetime
import sqlite3
import sys

with sqlite3.connect('venv/database.db') as db:
    cursor = db.cursor()
    query = """  CREATE TABLE IF NOT EXISTS expenses(Name TEXT, Surname TEXT, Patronymic TEXT, City TEXT, Balance INTEGER, Currency TEXT, Blocked INTEGER)  """
    cursor.execute(query)
    cursor.execute(""" CREATE TABLE IF NOT EXISTS History (Name TEXT, Surname TEXT, Date DATETIME, Event TEXT) """)


# Вывод на экран навигационного меню
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
    operations = [balance_print, set_money, get_money, transfer_money, blocked_or_unblocked_account, print_history,
                  exit_account]
    print(operations[message - 1]())


# Добавление в базу данных нового пользователя
def add_to_database(name_x, last_name_x):
    middle_name = input('Введите пожалуйста ваше отчество: ')
    city = input('Введите пожалуйста ваш город проживания: ')
    currency = input('Введите пожалуйста в какой валюте хранить ваши сбережения: ')
    try:
        cursor.execute(
            """  INSERT INTO expenses(name, surname, patronymic, city, balance, currency, blocked) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s') """ % (
                name_x, last_name_x, middle_name, city, 0, currency, 0))
        print('Новый пользователь успешно добавлен')
        db.commit()
        print_message()
    except sqlite3.Error as error:
        print('Ошибка при работе с SQLite', error)


# Проверка счёта на блокировку/не блокировку
def check_blocked_account():
    info = cursor.execute(
        """ SELECT blocked FROM expenses WHERE name = '%s' and surname = '%s' """ % (owner_name, last_name))
    x = info.fetchall()
    if bool(x[0][0]) == 0:
        return True
    else:
        return False


# Печать информации о пользователе и его счёте
def balance_print():
    info = cursor.execute(""" SELECT * FROM expenses WHERE surname='%s' and name='%s' """ % (last_name, owner_name))
    result = info.fetchall()
    for row in result:
        print(f'Имя: {row[0]}')
        print(f'Фамилия: {row[1]}')
        print(f'Ваш баланс состовляет: {row[4]}')
        print(f'Валюта: {row[5]}')
    print_message()


# Пополнение кошелька
def set_money():
    try:
        if check_blocked_account():
            cursor = db.cursor()
            x = int(input('Введите сумму которую вы хотите внести: '))
            cursor.execute(""" Update expenses set balance = balance + '%s' WHERE name = '%s' and surname = '%s' """ % (
                x, owner_name, last_name))
            add_history(f"Пополнение счёта {last_name} {owner_name}, Сумма пополнения {x}")
            db.commit()
            print('Пополнение кошелька прошла успешно!')
            cursor.close()
            print_message()
        else:
            print('''Ваш аккаунт заблокирован!''')
            print_message()
    except sqlite3.Error as error:
        print('Ошибка при работе с SQLite', error)


# "Снятие" наличных
def get_money():
    try:
        if check_blocked_account():
            cursor = db.cursor()
            x = int(input('Введите сумму которую вы хотите снять: '))
            info = cursor.execute(
                """ SELECT balance FROM expenses WHERE name='%s' and surname = '%s'""" % (owner_name, last_name))
            y = info.fetchone()
            db.commit()
            if x < y[0]:
                cursor.execute(
                    """ Update expenses set balance = balance - '%s' WHERE name = '%s' and surname = '%s' """ % (
                        x, owner_name, last_name))
                add_history(f"Снятие наличных со счёта {last_name} {owner_name}. Сумма {x}")
                db.commit()
                print('Выдача наличных прошла успешно!')
            else:
                print('Недостаточно средств на счёте!')
                add_history(f"Снятие наличных со счёта {last_name} {owner_name} откланён. Недостаточно средств на счёте!")
            cursor.close()
            print_message()
        else:
            print('''Ваш аккаунт заблокирован!''')
            print_message()
    except sqlite3.Error as error:
        print('Ошибка при работе с SQLite', error)


# Перевод денежных средств на другой счёт
def transfer_money():
    try:
        if check_blocked_account():
            cur = db.cursor()
            x = int(input('Введите сумму которую вы хотите перевести: '))
            user_surname_to = input('Введите фамилию пользователя, которому нужно перевести деньги: ')
            username_to = input('Введите имя: ')

            if (username_to == owner_name) and (user_surname_to == last_name):
                print("Нельзя перевести самому себе!")
                print_message()
            else:
                info = cur.execute(
                    """ SELECT balance FROM expenses WHERE name='%s' and surname='%s' """ % (owner_name, last_name))
                info_user_out = info.fetchone()

                info_user_to = cur.execute(
                    """ SELECT * FROM expenses WHERE name='%s' and surname='%s' """ % (username_to, user_surname_to))

                if not info_user_to:
                    add_history(f"Перевод c кошелька {last_name} {owner_name} на {user_surname_to} {username_to} откланён. Пользователь, которому вы хотите перевести не найден!")
                    print('Проверьте правильность введёного имени! Мы не смогли найти данного пользователя в базе данных.')
                elif x <= info_user_out[0]:
                    cur.execute(
                        """ Update expenses set balance = balance + '%s' WHERE name = '%s' and surname='%s' """ % (
                            x, username_to, user_surname_to))
                    cur.execute(
                        """ Update expenses set balance = balance - '%s' WHERE name = '%s' and surname='%s' """ % (
                            x, owner_name, last_name))
                    db.commit()
                    print('Перевод денег на другой счёт прошёл успешно!')
                    add_history(f"Перевод c кошелька {last_name} {owner_name} на {user_surname_to} {username_to} сумма перевода: {x}")
                else:
                    print('Недостаточно средств на счёте!')
                    add_history(f"Перевод c кошелька {last_name} {owner_name} на {user_surname_to} {username_to} откланён. Недостаточно средств на счёте!")
                cur.close()
                print_message()
        else:
            print('Ваш аккаунт заблокирован!')
            print_message()
    except sqlite3.Error as error:
        print('Ошибка при работе с SQLite', error)


# Блокировка\Разблокировка счёта
def blocked_or_unblocked_account():
    if not check_blocked_account():
        x = str(input('Вы хотите разблокировать свой счёт? '))
        if x in ['Yes', 'Да', 'yes', 'да']:
            cursor.execute(""" Update expenses set blocked = '%s' WHERE name = '%s' and surname='%s' """ % (
                0, owner_name, last_name))
            add_history('Счёт разблокирован.')
            db.commit()
            print('Ваш счёт успешно разблокирован.')
            print_message()
    else:
        x = str(input('Вы действительно хотите заблокировать свой счёт? '))
        if x in ['Yes', 'Да', 'yes', 'да']:
            cursor.execute(""" Update expenses set blocked = '%s' where name = '%s' and surname='%s' """ % (
                1, owner_name, last_name))
            add_history('Счёт заблокирован.')
            db.commit()
            print('Ваш счёт успешно заблокирован.')
            print_message()


# Вывод в консоль контекстное меню
def print_history():
    message = int(input('''Напишите пожалуйста какую информатцию вы хотите посмотреть:
                                    1. Посмотреть всю историю.
                                    2. Посмотреть только пополнения счёта.
                                    3. Посмотреть только снятия наличных со счёта.
                                    4. Посмотреть только переводы.
                                    '''))
    operations = [pr_hs_all, pr_hs_set, pr_hs_get, pr_hs_transfer]
    print(operations[message - 1]())


# Печать всей историй
def pr_hs_all():
    info = cursor.execute(""" SELECT * FROM History """)
    for i in info.fetchall():
        if (i[0] == last_name) and (i[1] == owner_name):
            print(f'{i[2]}, {i[3]} \n')
    print_message()


# Печть только истории пополнений
def pr_hs_set():
    info = cursor.execute(""" SELECT * FROM History """)
    for i in info.fetchall():
        if (i[0] == last_name) and (i[1] == owner_name) and ('Пополнение' in i[3]):
            print(f'{i[2]}, {i[3]} \n')
    print_message()


# Печть только истории снятий наличных
def pr_hs_get():
    info = cursor.execute(""" SELECT * FROM History """)
    for i in info.fetchall():
        if (i[0] == last_name) and (i[1] == owner_name) and ('Снятие' in i[3]):
            print(f'{i[2]}, {i[3]} \n')
    print_message()


# Печть только истории переводов
def pr_hs_transfer():
    info = cursor.execute(""" SELECT * FROM History """)
    for i in info.fetchall():
        if (i[0] == last_name) and (i[1] == owner_name) and ('Перевод' in i[3]):
            print(f'{i[2]}, {i[3]} \n')
    print_message()


# Выход из аккаунта
def exit_account():
    sys.exit(0)


# Добавление новой истории
def add_history(s):
    cursor.execute(
        """  INSERT INTO history(name, surname, date, event) VALUES('%s', '%s', '%s', '%s') """ % (
            last_name, owner_name, datetime.datetime.now().strftime('%d/%m/%Y %H:%M'), s))


# Вход в аккаунт
last_name = input('Здравствуйте,\nВведите пожалуйста вашу фамилию: ')
owner_name = input('Введите пожалуйста ваше имя: ')

# Проверка введенных данных
info = cursor.execute(""" SELECT * FROM expenses WHERE name = '%s' and surname = '%s' """ % (owner_name, last_name))
if info.fetchone() is None:
    # Выполняется при отсутствии пользователя в базе данных
    add_to_database(owner_name, last_name)
else:
    # Выполнятся при наличии пользователя в базе данных
    print_message()