import json
import time
from threading import Thread
import requests
from flask import request
import logging
import hmac
import hashlib
import base64
import os

import config

from __main__ import app

line_receivers = json.loads(os.getenv("LINE_TEST_USER"))


def test(user_number):
    time.sleep(10)
    for i in range(3):
        send_text(user_number, "Hello World!")

    for file_type, url, preview_url, duration in config.attachments_urls_line:
        send_media(user_number, file_type, url, preview_url, duration)


def handle_message(sender_id, received_message):
    if sender_id in line_receivers:
        if 'text' == received_message['type']:
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
               'Authorization': 'Bearer {}'.format(os.getenv('LINE_TOKEN'))}
    r = requests.post('https://api.line.me/v2/bot/message/push', json=payload, headers=headers)
    logging.debug(r.text)


def send_text(user_id, msg):
    payload = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": msg
            }]
    }
    call_send_api(payload)


def send_media(user_number, media_type, media_url, preview_url, duration):
    payload = {
        'to': user_number,
        'messages': [
            {
                'type': media_type,
                'originalContentUrl': media_url,
                'previewImageUrl' if preview_url else '': preview_url,    # max 1MB
                'duration' if duration else '': duration
            }]
    }
    call_send_api(payload)


def verify_webhook_call(payload, received_hash):
    new_hash = hmac.new(os.getenv('LINE_CHANNEL_SECRET').encode('utf-8'),
                        payload,
                        hashlib.sha256).digest()
    signature = base64.b64encode(new_hash).decode('utf-8')
    return received_hash == signature


@app.route('/line_webhook', methods=["POST"])
def line_webhook_post():
    data = request.data
    body = json.loads(data.decode('utf-8'))

    if not verify_webhook_call(request.get_data(), request.headers.get('x-line-signature')):
        logging.warning('webhook call not verified')
        return 'error', 403

    if 'events' in body:
        if not body['events']:
            logging.debug('line webhook set')
        else:
            event = body['events'][0]
            if event['type'] == 'message':
                sender_id = event['source']['userId']
                logging.debug('Sender Number: {}'.format(sender_id))
                handle_message(sender_id, event['message'])

        return 'ok', 200

    return 'error', 404
