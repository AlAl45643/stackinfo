import requests
from stem import Signal
from stem.control import Controller
import json
import psycopg as ps


def get_tor_session():
    session = requests.session()
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    return session


def renew_connection():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password="password")
        controller.signal(Signal.NEWNYM)

session = get_tor_session()
url = "https://emcins.wd5.myworkdayjobs.com/wday/cxs/emcins/EMC_Careers/jobs"

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "referer": "https://emcins.wd5.myworkdayjobs.com/en-US/EMC_Career/jobs",
}

session = get_tor_session()
response = session.request("POST", url, headers=headers)
result1 = json.loads(response.text)

conn = ps.connect(
    "dbname='dockerdjango' user='dbuser' host='127.0.0.1' password='dbpassword' port='5432'")
cur = conn.cursor()

for posting in result1['jobPostings']:
    remote = posting.get('remoteType', False)
    if remote:
        cur.execute(f"SELECT * FROM remote WHERE remote_text = '{remote}';")
        res = cur.fetchall()
        if res != []:
            print(res[0][2])
        else:
            print(remote)
            inp = input("Is this remote (y or n)")
            if inp == 'y':
                cur.execute(
                    "INSERT INTO remote (remote_text, is_remote) VALUES (%s, %s);", (remote, True))
            else:
                cur.execute(
                    "INSERT INTO remote (remote_text, is_remote) VALUES (%s, %s);", (remote, False))

conn.commit()
cur.close()
conn.close()
