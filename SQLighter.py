# -*- coding: utf-8 -*-
import sqlite3
from random import shuffle

from telebot import types


class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def select_work(self, user_id):
        """Получаем один элемент из БД"""
        with self.connection:
            return self.cursor.execute('SELECT work_time FROM user_data where user_id = ?',
                                       (user_id,))

    def select_rest(self, user_id):
        """Получаем один элемент из БД"""
        with self.connection:
            return self.cursor.execute('SELECT rest_time FROM user_data where user_id = ?',
                                       (user_id,))

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


def select_item_work(self, user_id, item):
    """Получаем один элемент из БД"""
    with self.connection:
        return self.cursor.execute('SELECT ? FROM data where data.user = ?',
                                   (item, user_id))
