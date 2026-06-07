import socket
import requests
import time
import json
import re
from datetime import datetime


LOGIN_URL = "http://10.10.42.3:801/eportal/portal/login"


# 读取配置
with open("config.json", encoding="utf-8") as f:
    cfg = json.load(f)

USERNAME = cfg["username"]
PASSWORD = cfg["password"]
CHECK_INTERVAL = cfg.get("check_interval", 60)


def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    line = f"[{now}] {msg}"

    print(line)

    with open("campus.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def get_local_ip():

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]

    finally:
        s.close()

    return ip


def login():

    ip = get_local_ip()

    params = {
        "callback": "dr1003",
        "login_method": "1",
        "user_account": USERNAME,
        "user_password": PASSWORD,
        "wlan_user_ip": ip,
        "wlan_user_ipv6": "",
        "wlan_user_mac": "000000000000",
        "wlan_ac_ip": "",
        "wlan_ac_name": "",
        "jsVersion": "4.2.1",
        "terminal_type": "1",
        "lang": "zh-cn",
        "v": "10390"
    }

    try:

        r = requests.get(
            LOGIN_URL,
            params=params,
            timeout=10
        )

        m = re.search(r'dr1003\((.*)\)', r.text)

        if m:

            data = json.loads(m.group(1))

            result = data["result"]
            msg = data["msg"]

            if result == 1:
                log("认证成功")

            else:
                log(f"认证失败：{msg}")

        else:
            log("服务器返回异常")

    except Exception as e:

        log(f"登录异常：{e}")


def network_ok():

    try:
        requests.get(
            "https://www.baidu.com",
            timeout=3
        )

        return True

    except:
        return False


log("北京交通大学校园网自动登录器启动")

while True:

    if network_ok():

        pass

    else:

        log("网络断开，开始重新认证")

        login()

    time.sleep(CHECK_INTERVAL)