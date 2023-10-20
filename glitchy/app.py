import os
import random
import time
from threading import Thread
import csv
import json
from datetime import datetime

from flask import Flask, send_from_directory, make_response
from waitress import serve
import logging
from dotenv import load_dotenv

import config

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

# all imports are needed for Flask app
from providers import facebook, whatsapp, telegram


@app.route("/static/<name>", methods=["GET"])
def host_file(name):
    extension = name.split(".")[-1]
    response = make_response(send_from_directory('./static', name, as_attachment=False))

    if extension == "mp4":
        response.headers['Content-Type'] = 'video/mp4'
    elif extension == "pdf":
        response.headers['Content-Type'] = 'application/pdf'
    elif extension == "mp3":
        response.headers['Content-Type'] = 'audio/mpeg'
    elif extension == "jpg":
        response.headers['Content-Type'] = 'image/jpeg'
    return response


def execute_part(results, index, kind, func, receiver, content, size_indicator, delay, no_of_msgs):
    counter = 0
    success_counter = 0
    for i in range(no_of_msgs):
        time.sleep(delay)
        res = func(receiver, content[size_indicator], kind)
        if res == 200:
            success_counter += 1
        else:
            print("Error: {}".format(res))
        counter += 1

    results[index] = (counter, success_counter)


def distribute_messages(no_of_msgs, thread_num):
    msg_per_thread = no_of_msgs // thread_num
    msg_per_thread_arr = [msg_per_thread] * thread_num

    if no_of_msgs % thread_num != 0:
        for i in range(no_of_msgs % thread_num):
            msg_per_thread_arr[i] += 1

    return msg_per_thread_arr


def multi_threaded_runner(size_indicator, idle_time, no_of_msgs,
                          provider, kind, func, receiver, content, delay, thread_num=1):
    curr_time = datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S UTC")
    print("{}: Starting {} {} test ...".format(curr_time, provider, kind))
    results = [(0, 0)] * thread_num
    threads = []
    msg_per_thread_arr = distribute_messages(no_of_msgs, thread_num)

    start_time = time.time()
    for i in range(thread_num):
        thread = Thread(target=execute_part, args=(results,
                                                   i,
                                                   kind,
                                                   func,
                                                   receiver,
                                                   content,
                                                   size_indicator,
                                                   delay,
                                                   msg_per_thread_arr[i]))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    execution_time = int(time.time() - start_time)
    total_trials = sum(int(tup[0]) for tup in results)
    total_success = sum(int(tup[1]) for tup in results)

    curr_time = datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S UTC")
    print("{}: {} tried {} {} messages of size {}, succeeded {}, took {}s".format(curr_time,
                                                                                  provider,
                                                                                  total_trials,
                                                                                  kind,
                                                                                  size_indicator,
                                                                                  total_success,
                                                                                  execution_time))

    # introduce an idle time between tests
    time.sleep(idle_time)
    return execution_time


def execute_test(receiver_id, size_indicator, app_indicator, idle_time=120, repetitions=10, no_of_msgs=72):
    results = []

    tg_receivers = json.loads(os.environ.get("TG_TEST_CHAT"))
    fb_receivers = json.loads(os.environ.get("FB_TEST_ID"))
    wa_receivers = json.loads(os.environ.get("WA_TEST_NO"))

    # provider, kind, function to exec, receiver, content/media to use, delay factor for the API, num of threads
    tests = [("Telegram", "text", telegram.send_text, tg_receivers[receiver_id], config.text_content, 0.6, 1),
             ("Messenger", "text", facebook.send_text, fb_receivers[receiver_id], config.text_content, 0.1, 1),
             ("WhatsApp", "text", whatsapp.send_text, wa_receivers[receiver_id], config.text_content, 0.3, 1),
             ("Telegram", "image", telegram.send_media, tg_receivers[receiver_id], config.image_urls, 0.6, 1),
             ("Messenger", "image", facebook.send_media, fb_receivers[receiver_id], config.image_urls, 0.3, 3),
             ("WhatsApp", "image", whatsapp.send_media, wa_receivers[receiver_id], config.image_urls, 0.3, 1),
             ("Telegram", "video", telegram.send_media, tg_receivers[receiver_id], config.video_urls, 0.6, 1),
             ("Messenger", "video", facebook.send_media, fb_receivers[receiver_id], config.video_urls, 0.6, 18),
             ("WhatsApp", "video", whatsapp.send_media, wa_receivers[receiver_id], config.video_urls, 0.3, 1),
             ("Telegram", "file", telegram.send_media, tg_receivers[receiver_id], config.file_urls, 0.6, 1),
             ("Messenger", "file", facebook.send_media, fb_receivers[receiver_id], config.file_urls, 0.15, 3),
             ("WhatsApp", "file", whatsapp.send_media, wa_receivers[receiver_id], config.file_urls, 0.25, 1),
             ("Telegram", "audio", telegram.send_media, tg_receivers[receiver_id], config.audio_urls, 0.6, 1),
             ("Messenger", "audio", facebook.send_media, fb_receivers[receiver_id], config.audio_urls, 0, 4),
             ("WhatsApp", "audio", whatsapp.send_media, wa_receivers[receiver_id], config.audio_urls, 0.25, 1)]

    # filter test to run only the ones for the given app
    # we only match by the first letter of the app name and parameter given
    filtered_tests = [test for test in tests if test[0][0].lower() == app_indicator[0].lower()]

    # we do X repetitions of the tests run
    for i in range(repetitions):
        print("Running test loop no {} ...".format(i))
        # randomize the order of tests
        random.shuffle(filtered_tests)

        # run all 15 tests
        for test in filtered_tests:
            curr_time = datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S UTC")
            # results format: repetition_no, start_time, provider, kind, size, execution_duration, end_time
            results.append((i, curr_time, test[0], test[1], size_indicator,
                            multi_threaded_runner(size_indicator, idle_time, no_of_msgs,
                                                  test[0], test[1], test[2], test[3], test[4], test[5], int(test[6])),
                            datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S UTC")))

    print("Saving results to file results_{}_size{}.csv ...".format(app_indicator, size_indicator))
    with open("results_{}_size{}.csv".format(app_indicator, size_indicator), mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["repetition_no", "start_time", "provider", "kind", "size", "execution_duration", "end_time"])
        for item in results:
            writer.writerow(item)


def setup_webhooks():
    telegram.set_webhook()
    viber.set_webhook()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5555))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() in ('true', '1')
    is_cloud = os.environ.get('CLOUD', 'False').lower() in ('true', '1')

    if is_cloud:
        if debug:
            logging.basicConfig(level=logging.DEBUG)
            setup_webhooks()
            app.run(host=host, port=port, debug=False)
        else:
            setup_webhooks()
            serve(app, host=host, port=port)
    else:
        if debug:
            logging.basicConfig(level=logging.DEBUG)

        # ______EXPERIMENT______

        # receiver_id=0 -> Maciej
        # receiver_id=1 -> Test Phone From GreenLab
        # receiver_id=2 -> Efe

        # NEED CHANGES FOR EACH RUN
        # size_indicator=0 -> AVAILABLE VALUES: 0 or 1 or 2
        # app_indicator="msg" -> AVAILABLE VALUES: "msg", "wa", "tg"

        # idle_time=120 -> no idle time between tests, default: 120 seconds
        # repetitions=10 -> number of repetitions of the tests, default: 10
        # no_of_msgs=72 -> number of messages sent in each trial, default: 72
        execute_test(receiver_id=1,
                     size_indicator=0, app_indicator="msg",
                     idle_time=120, repetitions=10, no_of_msgs=72)
