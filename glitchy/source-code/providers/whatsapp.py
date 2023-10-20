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

wa_receivers = json.loads(os.getenv("WA_TEST_NO"))


def test(user_number):
    time.sleep(10)
    for i in range(3):
        send_text(user_number, "Hello World!")

    for file_type, url in config.attachments_urls:
        send_media(user_number, url, file_type)


def handle_message(sender_number, received_message):
    if sender_number in wa_receivers:
        if 'body' in received_message:
            msg = received_message['body']
            send_text(sender_number, 'You just sent: {}'.format(msg))

            if msg.strip().lower() == 'start test':
                send_text(sender_number, 'OK, pls wait 10s')
                for i in range(3):
                    thread = Thread(target=test, args=(sender_number,))
                    thread.start()

        else:
            send_text(sender_number, 'This chatbot only accepts text messages')


def call_send_api(payload):
    headers = {'content-type': 'application/json',
               'Authorization': 'Bearer {}'.format(os.getenv('WA_TOKEN'))}
    url = 'https://graph.facebook.com/v17.0/{}/messages'.format(os.getenv("WA_PHONE_ID"))
    r = requests.post(url, json=payload, headers=headers)
    logging.debug(r.text)
    return r.status_code


def send_text(user_number, msg, _=None):
    payload = {
        'messaging_product': 'whatsapp',
        'to': user_number,
        'type': 'text',
        'text': {
            'preview_url': '',
            'body': msg
        }
    }
    return call_send_api(payload)


def send_media(user_number, media_url, media_type):
    if media_type == 'file':
        media_type = 'document'
    payload = {
        'messaging_product': 'whatsapp',
        'to': user_number,
        'type': media_type,
        media_type: {
            "link": media_url
        }
    }
    return call_send_api(payload)


# def wa_send_template(user_number, template):
#     payload = {
#         'messaging_product': 'whatsapp',
#         'to': user_number,
#         'type': 'template',
#         "template": {
#             "name": template,
#             "language": {
#                 "code": "en_US"
#             }
#         }
#     }
#     return call_wa_send_api(payload)


@app.route('/wa_webhook', methods=["GET"])
def wa_webhook_get():
    if 'hub.mode' in request.args and 'hub.verify_token' in request.args and 'hub.challenge' in request.args:
        mode = request.args.get('hub.mode')
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and verify_token == os.getenv("WA_VERIFY_TOKEN"):
            logging.debug('wa webhook verified')
            return challenge, 200

    return 'error', 403


def verify_webhook_call(payload, received_hash):
    signature = hmac.new(
        key=bytes(os.getenv('WA_APP_SECRET'), 'utf-8'),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()
    return received_hash == 'sha256=' + signature


@app.route('/wa_webhook', methods=["POST"])
def wa_webhook_post():
    data = request.data
    body = json.loads(data.decode('utf-8'))

    if not verify_webhook_call(request.get_data(), request.headers.get('X-Hub-Signature-256')):
        logging.warning('webhook call not verified')
        return 'error', 403

    if 'object' in body and body['object'] == 'whatsapp_business_account':
        entries = body['entry']
        for entry in entries:
            changes = entry['changes']

            for change in changes:
                if 'messages' in change['value']:
                    webhook_event = change['value']['messages'][0]
                    sender_number = webhook_event['from']
                    logging.debug('Sender Number: {}'.format(sender_number))

                    if 'text' in webhook_event:
                        handle_message(sender_number, webhook_event['text'])

                if 'statuses' in change['value']:
                    webhook_event = change['value']['statuses'][0]
                    if 'errors' in webhook_event:
                        logging.warning(webhook_event['errors'][0])

        return 'ok', 200

    return 'error', 404
