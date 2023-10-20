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

fb_receivers = json.loads(os.getenv("FB_TEST_ID"))


def test(sender_id, use_ids=False):
    time.sleep(10)

    for i in range(3):
        send_text(sender_id, 'Hello World!')

    if use_ids:
        for file_type, attachment_id in config.attachments_ids_fb:
            send_media_2(sender_id, file_type, attachment_id, use_ids)
    else:
        for file_type, url in config.attachments_urls:
            send_media_2(sender_id, file_type, url, use_ids)


def handle_message(sender_id, received_message):
    if sender_id in fb_receivers:
        if 'text' in received_message:
            msg = received_message['text']
            send_text(sender_id, 'You just sent: {}'.format(msg))

            if msg.strip().lower() == 'start test':
                send_text(sender_id, 'OK, pls wait 10s')
                for i in range(3):
                    thread = Thread(target=test, args=(sender_id,))
                    thread.start()

            if msg.strip().lower() == 'start test ids':
                send_text(sender_id, 'OK, pls wait 10s')
                for i in range(3):
                    thread = Thread(target=test, args=(sender_id, True))
                    thread.start()

            if msg.strip().lower() == 'upload media':
                send_text(sender_id, 'OK, uploading...')
                upload_media(sender_id)

        else:
            send_text(sender_id, 'This chatbot only accepts text messages')


def call_upload_api(file_type, file_url, is_reusable='true'):
    payload = {
        'access_token': os.getenv('FB_PAGE_TOKEN'),
        'message': {
            'attachment': {
                'type': file_type,
                'payload': {
                    'url': file_url,
                    'is_reusable': is_reusable
                }
            }
        }
    }
    headers = {'content-type': 'application/json'}

    url = 'https://graph.facebook.com/v17.0/{}/message_attachments'.format(os.getenv("FB_PAGE_ID"))
    r = requests.post(url, json=payload, headers=headers)
    logging.debug(r.text)
    return json.loads(r.text)['attachment_id']


def upload_media(sender_id):
    new_attachments = []

    for file_type, url in config.attachments_urls:
        new_attachments.append((file_type, call_upload_api(file_type, url)))

    logging.debug(new_attachments)
    send_text(sender_id, 'media uploaded: {}'.format(new_attachments))


def call_send_api(payload):
    headers = {'content-type': 'application/json'}
    url = 'https://graph.facebook.com/v17.0/{}/messages'.format(os.getenv("FB_PAGE_ID"))
    r = requests.post(url, json=payload, headers=headers)
    logging.debug(r.text)
    return r.status_code


def send_text_2(user_id, msg, messaging_type='RESPONSE'):
    payload = {
        'access_token': os.getenv('FB_PAGE_TOKEN'),
        'recipient': {'id': user_id},
        'message': {"text": msg},
        'messaging_type': messaging_type
    }
    return call_send_api(payload)


def send_text(user_id, msg, _=None):
    return send_text_2(user_id, msg)


def send_media_2(user_id, media_type, media_ref, use_ids, messaging_type='RESPONSE'):
    payload = {
        'access_token': os.getenv('FB_PAGE_TOKEN'),
        'recipient': {'id': user_id},
        'message': {
            'attachment': {
                'type': media_type,
                'payload': {
                    'attachment_id' if use_ids else 'url': media_ref,
                }
            }
        },
        'messaging_type': messaging_type
    }
    return call_send_api(payload)


def send_media(user_id, media_ref, media_type):
    return send_media_2(user_id, media_type, media_ref, False)


@app.route('/fb_webhook', methods=["GET"])
def fb_webhook_get():
    if 'hub.mode' in request.args and 'hub.verify_token' in request.args and 'hub.challenge' in request.args:
        mode = request.args.get('hub.mode')
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and verify_token == os.getenv("FB_VERIFY_TOKEN"):
            logging.debug('fb webhook verified')
            return challenge, 200

    return 'error', 403


def verify_webhook_call(payload, received_hash):
    signature = hmac.new(
        key=bytes(os.getenv('FB_APP_SECRET'), 'utf-8'),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()
    return received_hash == 'sha256=' + signature


@app.route('/fb_webhook', methods=["POST"])
def fb_webhook_post():
    data = request.data
    body = json.loads(data.decode('utf-8'))

    if not verify_webhook_call(request.get_data(), request.headers.get('X-Hub-Signature-256')):
        logging.warning('webhook call not verified')
        return 'error', 403

    if 'object' in body and body['object'] == 'page':
        entries = body['entry']

        for entry in entries:
            webhook_event = entry['messaging'][0]
            sender_id = webhook_event['sender']['id']
            logging.debug('Sender ID: {}'.format(sender_id))

            if 'message' in webhook_event:
                handle_message(sender_id, webhook_event['message'])

        return 'OK', 200

    return 'error', 404
