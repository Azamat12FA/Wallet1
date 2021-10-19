from datetime import datetime

from main import *
from window_function import *


def print_history():
    message = int(input('''Напишите пожалуйста какую информатцию вы хотите посмотреть:
                                    1. Посмотреть всю историю.
                                    2. Посмотреть только пополнения счёта.
                                    3. Посмотреть только снятия наличных со счёта.
                                    4. Посмотреть только переводы.
                                    '''))
    operations = [pr_hs_all, pr_hs_set, pr_hs_get, pr_hs_transfer]
    print(operations[message - 1]())


def pr_hs_all():
    info = cursor.execute(""" SELECT * FROM History """)
    for i in info.fetchall():
        if (i[0] == last_name) and (i[1] == owner_name):
            print(f'{i[2]}, {i[3]} \n')
    window_function.print_message()


def pr_hs_set():
    info = cursor.execute(""" SELECT * FROM History """)
    for i in info.fetchall():
        if (i[0] == last_name) and (i[1] == owner_name) and ('Пополнение' in i[3]):
            print(f'{i[2]}, {i[3]} \n')
    window_function.print_message()


def pr_hs_get():
    info = cursor.execute(""" SELECT * FROM History """)
    for i in info.fetchall():
        if (i[0] == last_name) and (i[1] == owner_name) and ('Снятие' in i[3]):
            print(f'{i[2]}, {i[3]} \n')
    window_function.print_message()


def pr_hs_transfer():
    info = cursor.execute(""" SELECT * FROM History """)
    for i in info.fetchall():
        if (i[0] == last_name) and (i[1] == owner_name) and ('Перевод' in i[3]):
            print(f'{i[2]}, {i[3]} \n')
    window_function.print_message()


def add_history(s):
    cursor.execute(
        """  INSERT INTO history(name, surname, date, event) VALUES('%s', '%s', '%s', '%s') """ % (
            last_name, owner_name, datetime.now().strftime('%d/%m/%Y %H:%M'), s))
