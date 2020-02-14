# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с JSON и логами.
import json
import logging

# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request
app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

# Хранилище данных о сессиях.
sessionStorage = {}

# Подсказки
tips = []

@app.before_first_request
def initTips():
    logging.log(logging.INFO, 'Before first request')
    with open('tips.json', 'r') as f:
        loaded_json = json.load(f)
        for x in loaded_json:
            tips.append(Tip(x['name'], x['type'], x['confirm'], x['decline'], x['response']))


# Задаем параметры приложения Flask.
@app.route("/", methods=['POST'])

def main():
# Функция получает тело запроса и возвращает ответ.
    logging.info('Request: %r', request.json)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    handle_dialog(request.json, response)

    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )

# Задаем параметры приложения Flask.
@app.route("/", methods=['GET'])

def open_main():

    response = {
        "online": True
    }

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )

# Функция для непосредственной обработки диалога.
def handle_dialog(req, res):

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.

        res['response']['text'] = 'Добро пожаловать в навык с подсказками для игроков в Pathfinder. Спрашивай, что тебе интересно!'
        return

    # Ищем по типу и имени
    found_by_type_and_name = [x for x in tips if x.qualify_by_type_and_name(req['request']['command'].lower())]

    if len(found_by_type_and_name) == 1:
        # Если нашли конкретный - возвращаем
        res['response']['text'] = found_by_type_and_name[0].response
        return

    # Ищем по ключевым словам
    found_by_qualify = [x for x in tips if x.qualify(req['request']['command'].lower())]

    if len(found_by_qualify) == 1:
        # Если нашли только один - возвращаем его
        res['response']['text'] = found_by_qualify[0].response
        return

    if len(found_by_qualify) > 1:
        # Если нашли несколько - предлагаем уточнить
        res['response']['text'] = 'Возможно, вы имели ввиду: ' + '; '.join([x.type + ': ' + x.name for x in found_by_qualify])
        return

    # Если пришли сюда - ничего не нашли, надо уточнить запрос
    res['response']['text'] = 'Не понял вопрос. Попробуйте перефразировать'

    return


class Tip:

    def __init__(self, name, type, confirm, decline, response):
        self.name = name
        self.type = type
        self.confirm = confirm
        self.confirm = confirm
        self.decline = decline
        self.response = response

    def qualify(self, text):
        return any(x.lower() in text for x in self.confirm) and not any(x.lower() in text for x in self.decline)

    def qualify_by_type_and_name(self, text):
        return self.type.lower() + ' ' + self.name.lower() == text