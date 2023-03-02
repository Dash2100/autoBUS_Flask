from flask import Flask, request, redirect, jsonify, render_template
import os
import threading
import schedule
from bs4 import BeautifulSoup
import requests
import time
import json

stop_event = threading.Event()

#自動回報人
car = "A091"
stu_id = "01V582"

app = Flask(__name__, static_url_path='/static')

def lineNotify(msg):
    print(msg)
    token = 'lVk4U4xqG6aYVTO7NG4Rp9VhO4nDEzgInmNCFxu1jDi'
    headers = {"Authorization": "Bearer " + token}
    data = {'message': msg}
    requests.post("https://notify-api.line.me/api/notify",
                  headers=headers, data=data)

def log(msg):
    global log_msg
    print(msg)
    now = time.strftime("%H:%M:%S | ", time.localtime())
    log_msg.append(now + msg)


def task(car, stu_id):
    global error_times, return_msg
    if error_times >= 3:
        log("Error times exceed 3, exit.")
        return 0
    session_requests = requests.session()
    url = "https://app3.mingdao.edu.tw/traffic_b/action.php"

    data = {'hid1': '2',
            'txt1': '',
            'ck1': '否',
            'ck2': '是',
            'ck3': '是',
            'ck4': '否',
            'ck5': '否',
            'ck6': '否',
            'ck7': '是',
            'ck8': '否',
            'ck9': '是',
            'ck10': '否',
            'ck11': '否',
            'ck12': '否',
            'ck13': '否',
            'ck14': '否',
            'ck15': '否',
            'ck16': '否',
            'hid_caracc': car,
            'hid_study': stu_id,
            'okgo': '送出',
            }

    result = session_requests.post(url, data=data)
    html = BeautifulSoup(result.text, 'html.parser')
    return_msg = html.find(
        "p", style="margin:50px; text-align:center;").text.replace(" ", "").replace("\n", "")
    log("Website Response: " + return_msg)
    if return_msg != "操作成功。":
        error_times += 1
        log(f"Unexpected response ({error_times})")
        time.sleep(3)
        task(car, stu_id)
    else:
        log("Task finished.")


def runRequest(car, stu_id):
    global error_times, log_msg, return_msg
    error_times = 0
    log_msg = []
    log(f"Task start for {car} {stu_id}")

    # check status
    with open('settings.json', 'r') as f:
        settings = json.loads(f.read())

    if settings["status"] == "off":
        return_msg = "Task stopped because AutoBUS status is off."
        log(return_msg)
    else:
        task(car, stu_id)

    # save log
    with open('history.log', 'a') as f:
        f.write(time.strftime("[ %m/%d %a ]", time.localtime()))  # add date
        f.write('\n')
        for line in log_msg:
            f.write(line)
            f.write('\n')
        f.write('\n')

    # send line notify
    lineNotify(f'[{car} {stu_id}] {return_msg}')


# -- schedule --

def autorun():
    print("------------------------------------------")
    print("Script will run at 17:30 every Thursday.")
    print('Total Thread:', threading.active_count())
    print("------------------------------------------")
    schedule.every().thursday.at("17:30").do(runRequest, car, stu_id)
    while not stop_event.is_set():
        schedule.run_pending()
        time.sleep(1)


def threading_init():
    global AutoBUS_thread
    AutoBUS_thread = threading.Thread(
        target=autorun,
        name='AutoBUS'
    )
    AutoBUS_thread.start()

# -- web --

@app.route('/', methods=['GET'])
def index():
    with open('history.log', 'r') as f:
        history = f.read().splitlines()
    return render_template('index.html', history=history)

@app.route('/status', methods=['GET','POST'])
def status():
    if request.method == 'POST':
        with open('settings.json', 'r') as f:
            settings = json.loads(f.read())

        settings["status"] = request.get_json()['status']

        if settings["status"] == "on":
            lineNotify('Schedule on.')
        elif settings["status"] == "off":
            lineNotify('Schedule off.')
        else:
            return "error"

        with open('settings.json', 'w') as f:
            f.write(json.dumps(settings))

        return "ok"
    else:
        with open('settings.json', 'r') as f:
            settings = json.loads(f.read())
        return jsonify(settings)
    
@app.route('/manual', methods=['POST'])
def manual():
    cid = request.get_json()['car']
    sid = request.get_json()['stu_id']
    if cid == "default" and sid == "default":
        runRequest(car, stu_id)
    else:
        runRequest(cid, sid)
    return "ok"


if __name__ == '__main__':
    # threading_init()
    app.run(debug=True, host='0.0.0.0', port=8080)
    # app.run(host='0.0.0.0', port=8080)
    print("Terminating thread...")
    stop_event.set() # stop thread