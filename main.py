import sqlite3

import window_function

with sqlite3.connect('venv/database.db') as db:
    cursor = db.cursor()
    query = """  CREATE TABLE IF NOT EXISTS expenses(Name TEXT, Surname TEXT, Patronymic TEXT, City TEXT, Balance INTEGER, Currency TEXT, Blocked INTEGER)  """
    cursor.execute(query)
    cursor.execute(""" CREATE TABLE IF NOT EXISTS History (Name TEXT, Surname TEXT, Date DATETIME, Event TEXT) """)

# Вход в аккаунт
last_name = input('Здравствуйте,\nВведите пожалуйста вашу фамилию: ')
owner_name = input('Введите пожалуйста ваше имя: ')

# Проверка введенных данных
info = cursor.execute(""" SELECT * FROM expenses WHERE name = '%s' and surname = '%s' """ % (owner_name, last_name))
if info.fetchone() is None:

    # Выполняется при отсутствии пользователя в базе данных
    middle_name = input('Введите пожалуйста ваше отчество: ')
    city = input('Введите пожалуйста ваш город проживания: ')
    currency = input('Введите пожалуйста в какой валюте хранить ваши сбережения: ')
    window_function.add_to_database(owner_name, last_name, middle_name, city, 0, currency, 0)
else:
    # Выполнятся при наличии пользователя в базе данных
    window_function.print_message()
