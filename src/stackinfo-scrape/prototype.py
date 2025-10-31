import requests
from stem import Signal
from stem.control import Controller
import json


def get_tor_session():
    session = requests.session()
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    return session


def renew_connection():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password="password")
        controller.signal(Signal.NEWNYM)


url = "https://emcins.wd5.myworkdayjobs.com/wday/cxs/emcins/EMC_Careers/jobs"

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "referer": "https://emcins.wd5.myworkdayjobs.com/en-US/EMC_Career/jobs",
}

session = get_tor_session()
response = session.request("POST", url, headers=headers)
result1 = json.loads(response.text)

url2 = "https://directv.wd1.myworkdayjobs.com/wday/cxs/directv/Careers/jobs"
headers2 = {
    "accept": "application/json",
    "content-type": "application/json",
    "referer": "https://directv.wd1.myworkdayjobs.com/en-US/Careers/",
}
response2 = session.request("POST", url2, headers=headers2)
result2 = json.loads(response2.text)

url3 = "https://att.wd1.myworkdayjobs.com/wday/cxs/att/ATTGeneral/jobs"
headers3 = {
    "accept": "application/json",
    "content-type": "application/json",
    "referer": "https://att.wd1.myworkdayjobs.com/en-US/ATTGeneral",
}
response3 = session.request("POST", url3, headers=headers3)
result3 = json.loads(response3.text)
