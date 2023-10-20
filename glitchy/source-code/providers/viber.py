import json
import time
from threading import Thread
import requests
from flask import request
import logging
import hmac
import hashlib
import os

import config

from __main__ import app

viber_receivers = json.loads(os.getenv("VIBER_TEST_SENDER"))


def test(sender_id):
    time.sleep(10)
    for i in range(3):
        send_text(sender_id, "Hello World!")

    for file_type, url, size, name in config.attachments_urls_viber:
        send_media(sender_id, file_type, url, size, name)


def handle_message(sender_id, received_message):
    if str(sender_id) in viber_receivers:
        if received_message['type'] == 'text':
            msg = received_message['text']
            send_text(sender_id, 'You just sent: {}'.format(msg))

            if msg.strip().lower() == 'start test':
                send_text(sender_id, 'OK, pls wait 10s')
                for i in range(3):
                    thread = Thread(target=test, args=(sender_id,))
                    thread.start()

        else:
            send_text(sender_id, 'This chatbot only accepts text messages')


def call_send_api(payload):
    headers = {'content-type': 'application/json',
               'X-Viber-Auth-Token': os.getenv('VIBER_TOKEN')}
    r = requests.post('https://chatapi.viber.com/pa/send_message', json=payload, headers=headers)
    logging.debug(r.text)


def send_text(sender_id, msg):
    payload = {
        'receiver': sender_id,
        'type': 'text',
        'text': msg,
        'sender': {'name': 'GreenLab'}
    }
    call_send_api(payload)


def send_media(sender_id, media_type, media_url, media_size=None, media_name=None):
    payload = {
        'receiver': sender_id,
        'type': media_type,
        'sender': {'name': 'GreenLab'},
        'media': media_url,
        'size' if media_size else '': media_size,
        'file_name' if media_name else '': media_name
    }
    call_send_api(payload)


def set_webhook():
    payload = {
        'url': '{}/viber_webhook'.format(config.HOSTING_URL),
        'send_name': 'true'
    }
    headers = {'content-type': 'application/json',
               'X-Viber-Auth-Token': os.getenv('VIBER_TOKEN')}
    r = requests.post('https://chatapi.viber.com/pa/set_webhook', json=payload, headers=headers)
    logging.debug(r.text)


def verify_webhook_call(payload, received_hash):
    signature = hmac.new(
        key=bytes(os.getenv('VIBER_TOKEN'), 'utf-8'),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()
    return received_hash == signature


@app.route('/viber_webhook', methods=["GET", "POST"])
def viber_webhook_get():
    data = request.data
    body = json.loads(data.decode('utf-8'))

    if not verify_webhook_call(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        logging.warning('webhook call not verified')
        return 'error', 403

    if 'event' in body:
        if body['event'] == 'webhook':
            logging.debug('viber webhook set')

        if body['event'] == 'message':
            message = body['message']
            sender_id = body['sender']['id']
            logging.debug('Sender ID: {}'.format(sender_id))
            handle_message(sender_id, message)

        return 'ok', 200

    return 'error', 404
