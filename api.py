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
            tips.append(Tip(x['confirm'], x['decline'], x['response']))


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
    user_id = req['session']['user_id']

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.

        res['response']['text'] = 'Добро пожаловать в навык с подсказками для игроков в Pathfinder. Спрашивай, что тебе интересно!'
        return

    tip = next((x for x in tips if x.qualify(req['request']['original_utterance'].lower())),
               Tip([],[], 'Вопрос не ясен, попробуйте перефразировать'))

    res['response']['text'] = tip.response()

    return


class Tip:

    def __init__(self, confirm, decline, response):
        self.confirm = confirm
        self.decline = decline
        self.response = response

    def qualify(self, text):
        return any(x in text for x in self.confirm) and not any(x in text for x in self.decline)

    def response(self):
        return self.response