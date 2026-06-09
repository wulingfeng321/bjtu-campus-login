import json
import re
import socket
import time
from datetime import datetime
from pathlib import Path

import requests


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"
LOG_PATH = BASE_DIR / "campus.log"

LOGIN_URL = "http://10.10.42.3:801/eportal/portal/login"
LOGIN_HOST = "10.10.42.3"
DEFAULT_CHECK_URL = "https://www.baidu.com"
DEFAULT_CHECK_INTERVAL = 60
DEFAULT_REQUEST_TIMEOUT = 10
DEFAULT_NETWORK_TIMEOUT = 3


# 读取配置
with CONFIG_PATH.open(encoding="utf-8") as f:
    cfg = json.load(f)

USERNAME = cfg["username"]
PASSWORD = cfg["password"]
CHECK_INTERVAL = max(int(cfg.get("check_interval", DEFAULT_CHECK_INTERVAL)), 5)
CHECK_URL = cfg.get("check_url", DEFAULT_CHECK_URL)
REQUEST_TIMEOUT = int(cfg.get("request_timeout", DEFAULT_REQUEST_TIMEOUT))
NETWORK_TIMEOUT = int(cfg.get("network_timeout", DEFAULT_NETWORK_TIMEOUT))
LOCAL_IP_PROBE_HOST = cfg.get("local_ip_probe_host", LOGIN_HOST)
WLAN_USER_MAC = cfg.get("wlan_user_mac", "000000000000")


def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{now}] {msg}"

    print(line, flush=True)

    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def get_local_ip(probe_host=LOCAL_IP_PROBE_HOST):
    """获取访问认证服务器时会使用的本机 IPv4 地址。"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # UDP connect 不会真正发包，但会让系统按路由表选择出口地址。
        # 使用校园网认证服务器而不是公网 DNS，可以避免树莓派未认证时没有公网路由导致取 IP 失败。
        s.connect((probe_host, 80))
        return s.getsockname()[0]
    finally:
        s.close()


def fallback_local_ip():
    """在路由探测失败时，从主机名解析结果中兜底选择一个非回环 IPv4。"""
    candidates = []

    try:
        hostname = socket.gethostname()
        candidates.append(socket.gethostbyname(hostname))
        for info in socket.getaddrinfo(hostname, None, socket.AF_INET):
            candidates.append(info[4][0])
    except OSError as exc:
        log(f"主机名解析本机 IP 失败：{exc}")

    for ip in candidates:
        if ip and not ip.startswith("127."):
            return ip

    return None


def login():
    try:
        try:
            ip = get_local_ip()
        except OSError as exc:
            log(f"通过路由探测本机 IP 失败：{exc}")
            ip = fallback_local_ip()

        if not ip:
            log("认证失败：无法获取本机 IPv4 地址，请检查树莓派是否已连接校园网网口/Wi-Fi")
            return False

        log(f"准备认证，本机 IP：{ip}")

        params = {
            "callback": "dr1003",
            "login_method": "1",
            "user_account": USERNAME,
            "user_password": PASSWORD,
            "wlan_user_ip": ip,
            "wlan_user_ipv6": "",
            "wlan_user_mac": WLAN_USER_MAC,
            "wlan_ac_ip": "",
            "wlan_ac_name": "",
            "jsVersion": "4.2.1",
            "terminal_type": "1",
            "lang": "zh-cn",
            "v": "10390",
        }

        r = requests.get(LOGIN_URL, params=params, timeout=REQUEST_TIMEOUT)
        log(f"认证接口 HTTP 状态码：{r.status_code}")

        m = re.search(r"dr1003\((.*)\)", r.text)

        if m:
            data = json.loads(m.group(1))
            result = data.get("result")
            msg = data.get("msg", "")

            if result == 1:
                log("认证成功")
                return True

            log(f"认证失败：{msg or data}")
            return False

        preview = r.text.replace("\n", " ")[:200]
        log(f"服务器返回异常：{preview}")
        return False

    except Exception as exc:
        log(f"登录异常：{exc}")
        return False


def network_ok():
    try:
        r = requests.get(CHECK_URL, timeout=NETWORK_TIMEOUT)
        return r.ok
    except requests.RequestException as exc:
        log(f"网络检测失败：{exc}")
        return False


def main():
    log("北京交通大学校园网自动登录器启动")

    while True:
        if not network_ok():
            log("网络断开，开始重新认证")
            login()

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
