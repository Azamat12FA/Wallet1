# Вывод на экран навигационного меню
import sys

from history_func import *


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
def add_to_database(name_x, last_name_x, middle_name_x, city_x, balance_x, currency_x, check_block_x):
    try:
        cursor.execute(
            """  INSERT INTO expenses(name, surname, patronymic, city, balance, currency, blocked) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s') """ % (
                name_x, last_name_x, middle_name_x, city_x, balance_x, currency_x, check_block_x))
        print('Новый пользователь успешно добавлен')
        db.commit()
        window_function.print_message()
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
    window_function.print_message()


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
            window_function.print_message()
        else:
            print('''Ваш аккаунт заблокирован!''')
            window_function.print_message()
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
            window_function.print_message()
        else:
            print('''Ваш аккаунт заблокирован!''')
            window_function.print_message()
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
                window_function.print_message()
            else:
                info = cur.execute(
                    """ SELECT balance FROM expenses WHERE name='%s' and surname='%s' """ % (owner_name, last_name))
                info_user_out = info.fetchone()

                info_user_to = cur.execute(
                    """ SELECT * FROM expenses WHERE name='%s' and surname='%s' """ % (username_to, user_surname_to))

                if not info_user_to:
                    add_history(f"Перевод c кошелька {last_name} {owner_name} на {user_surname_to} {username_to} откланён. Пользователь, которому вы хотите перевести не найден!")
                    print('Проверьте правильность введёного имени! Мы не смогли найти данного пользователя в базе данных.')
                elif x < info_user_out[0]:
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
                window_function.print_message()
        else:
            print('Ваш аккаунт заблокирован!')
            window_function.print_message()
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
            window_function.print_message()
    else:
        x = str(input('Вы действительно хотите заблокировать свой счёт? '))
        if x in ['Yes', 'Да', 'yes', 'да']:
            cursor.execute(""" Update expenses set blocked = '%s' where name = '%s' and surname='%s' """ % (
                1, owner_name, last_name))
            add_history('Счёт заблокирован.')
            db.commit()
            print('Ваш счёт успешно заблокирован.')
            window_function.print_message()


# Выход из аккаунта
def exit_account():
    sys.exit(0)
