"""Сохранение и загрузка партии в JSON файл"""

import json


def save_to_file(filename, data):
    """Записывает все данные партии в JSON файл"""
    file = open(filename, "w", encoding="utf-8")
    json.dump(data, file, ensure_ascii=False, indent=2)
    file.close()


def load_from_file(filename):
    """Читает данные партии из JSON файла и возвращает словарь"""
    file = open(filename, "r", encoding="utf-8")
    data = json.load(file)
    file.close()
    return data