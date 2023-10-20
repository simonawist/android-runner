import json
import time
from threading import Thread
import requests
from flask import request
import logging
import os

import config

from __main__ import app

tg_receivers = json.loads(os.getenv("TG_TEST_CHAT"))


def test(chat_id):
    time.sleep(10)
    for i in range(3):
        send_text(chat_id, "Hello World!")

    for file_type, url in config.attachments_urls:
        send_media(chat_id, url, file_type)


def handle_message(chat_id, received_message):
    if str(chat_id) in tg_receivers:
        if 'text' in received_message:
            msg = received_message['text']
            send_text(chat_id, 'You just sent: {}'.format(msg))

            if msg.strip().lower() == 'start test':
                send_text(chat_id, 'OK, pls wait 10s')
                for i in range(3):
                    thread = Thread(target=test, args=(chat_id,))
                    thread.start()

        else:
            send_text(chat_id, 'This chatbot only accepts text messages')


def call_send_api(payload, msg_type):
    headers = {'content-type': 'application/json'}
    url = 'https://api.telegram.org/bot{}/send{}'.format(os.getenv('TELEGRAM_BOT_TOKEN'), msg_type)
    r = requests.post(url, json=payload, headers=headers)
    logging.debug(r.text)
    return r.status_code


def send_text(chat_id, msg, _=None):
    payload = {
        'chat_id': chat_id,
        'text': msg
    }
    return call_send_api(payload, 'Message')


def send_media(chat_id, media_url, media_type):
    if media_type == 'file':
        media_type = 'document'
    if media_type == 'image':
        media_type = 'photo'
    payload = {
        'chat_id': chat_id,
        media_type: media_url
    }
    return call_send_api(payload, media_type.capitalize())


def set_webhook():
    payload = {
        'url': '{}/telegram_webhook'.format(config.HOSTING_URL),
        'secret_token': os.getenv("TELEGRAM_SECRET")
    }
    headers = {'content-type': 'application/json'}
    url = 'https://api.telegram.org/bot{}/setWebhook'.format(os.getenv('TELEGRAM_BOT_TOKEN'))
    r = requests.post(url, json=payload, headers=headers)
    logging.debug(r.text)


def verify_webhook_call(header):
    return header == os.getenv("TELEGRAM_SECRET")


@app.route('/telegram_webhook', methods=["GET", "POST"])
def telegram_webhook_get():
    data = request.data
    body = json.loads(data.decode('utf-8'))

    if not verify_webhook_call(request.headers.get('X-Telegram-Bot-Api-Secret-Token')):
        logging.warning('webhook call not verified')
        return 'error', 403

    if 'message' in body:
        message = body['message']
        chat_id = message['chat']['id']
        logging.debug('Sender Chat: {}'.format(chat_id))
        handle_message(chat_id, message)
        return 'ok', 200

    return 'error', 404
