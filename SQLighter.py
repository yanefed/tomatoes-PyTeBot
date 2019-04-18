# -*- coding: utf-8 -*-
import sqlite3
from random import shuffle

from telebot import types


class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def select_item(self, user_id, item):
        """Получаем один элемент из БД"""
        with self.connection:
            return self.cursor.execute('SELECT ? FROM user_data where data.user = ?',
                                       (item, user_id))

    def new_user(self, user_id):
        with self.connection:
            self.cursor.execute('INSERT INTO user_data VALUES (?, 25, 5)', (user_id,))

    def searh_user(self):
        with self.connection:
            return self.cursor.execute('SELECT user_id FROM user_data').fetchall()

    def select_all(self):
        """ Получаем все строки """
        with self.connection:
            return self.cursor.execute('SELECT * FROM music').fetchall()

    def select_single(self, rownum):
        """ Получаем одну строку с номером rownum """
        with self.connection:
            return self.cursor.execute('SELECT * FROM music WHERE id = ?', (rownum,)).fetchall()[0]

    def count_rows(self):
        """ Считаем количество строк """
        with self.connection:
            result = self.cursor.execute('SELECT * FROM music').fetchall()
            return len(result)

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()


def generate_markup(right_answer, wrong_answers):
    """
    Создаем кастомную клавиатуру для выбора ответа
    :param right_answer: Правильный ответ
    :param wrong_answers: Набор неправильных ответов
    :return: Объект кастомной клавиатуры
    """
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    # Склеиваем правильный ответ с неправильными
    all_answers = '{},{}'.format(right_answer, wrong_answers)
    # Создаем лист (массив) и записываем в него все элементы
    list_items = []
    for item in all_answers.split(','):
        list_items.append(item)
    # Хорошенько перемешаем все элементы
    shuffle(list_items)
    # Заполняем разметку перемешанными элементами
    for item in list_items:
        markup.add(item)
    return markup


def select_item(self, user_id, item):
    """Получаем один элемент из БД"""
    with self.connection:
        return self.cursor.execute('SELECT ? FROM data where data.user = ?',
                                   (item, user_id))
