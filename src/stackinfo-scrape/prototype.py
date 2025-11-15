import requests
from stem import Signal
from stem.control import Controller
import json
import pandas as pd
import psycopg as ps
import re


def get_tor_session():
    session = requests.session()
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    return session


def renew_connection():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password="password")
        controller.signal(Signal.NEWNYM)


def retrieve_workday(url, referer):
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "referer": f"{referer}",
    }
    session = get_tor_session()
    response = session.request("POST", url, headers=headers)
    result = json.loads(response.text)
    return result


def is_remote(cur, remote_text):
    if remote_text == False:
        return False
    cur.execute(f"SELECT * FROM remote WHERE remote_text = '{remote_text}';")
    res = cur.fetchall()
    if res != []:
        return res[0][2]
    else:
        print(remote_text)
        inp = input("Is this remote (y or n)")
        match inp:
            case 'y':
                cur.execute(
                    "INSERT INTO remote (remote_text, is_remote) VALUES (%s, %s);", (remote_text, True))
                return True
            case 'n':
                cur.execute(
                    "INSERT INTO remote (remote_text, is_remote) VALUES (%s, %s);", (remote_text, False))
                return False


def is_location_in_us(city, state):
    locations = pd.read_csv("./uscities.csv")
    for i in range(len(locations)):
        cities = locations['city']
        states = locations['admin_name']
        city_regex = re.compile(cities.iloc[i])
        state_regex = re.compile(states.iloc[i])
        city_res = re.search(city_regex, city)
        state_res = re.search(state_regex, state)
        if city_res and state_res:
            return True
    return False


def parse_for_locations(location_text):
    regex = re.compile(r"(?=((?:(?<=\b)(?:[A-Za-z.])+ ){0,3}(?<=\b)(?:[A-Za-z.])+,(?:(?: |)(?:[A-Za-z.])+){1,2}))")
    matches = re.findall(regex, location_text)
    return matches


url = "https://target.wd5.myworkdayjobs.com/wday/cxs/target/targetcareers/jobs"
referal = "https://target.wd5.myworkdayjobs.com/targetcareers"
json = retrieve_workday(url, referal)

database = "dbname='dockerdjango' user='dbuser' host='127.0.0.1' password='dbpassword' port='5432'"
with ps.connect(database) as conn:
    with conn.cursor() as cur:
        for posting in json['jobPostings']:
            remote_text = posting.get('remoteType', False)
            if is_remote(cur, remote_text): 
                print(f"Job posting is remote: {remote_text}")
                continue
            locations_text = posting.get('locationsText', False)
            print(parse_for_locations(locations_text), f"locationsText: {locations_text}")
            conn.commit()
