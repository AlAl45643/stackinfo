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


def retrieve_json(url, referer, method):
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "referer": f"{referer}",
    }
    session = get_tor_session()
    response = session.request(method, url, headers=headers)
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
    regex = re.compile(
        r"(?=((?:(?<=\b)(?:[A-Za-z.])+ ){0,3}(?<=\b)(?:[A-Za-z.])+,(?:(?: |)(?:[A-Za-z.])+){1,2}))")
    matches = re.findall(regex, location_text)
    return matches


def split_commas(string):
    regex = re.compile(r",")
    res = re.split(regex, string)
    return res


def ensure_state_full(state):
    abrev_to_state = {'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona',   'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana',
                      'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'}
    full_state = abrev_to_state.get(state, False)
    if full_state:
        return full_state
    else:
        return state


def get_last_link_part(link):
    regex = re.compile(r"[^/]+(?=$)")
    match = re.search(regex, link)
    res = match.group(0)
    return res


# url = "https://att.wd1.myworkdayjobs.com/wday/cxs/att/ATTGeneral/jobs"
# referal = https://att.wd1.myworkdayjobs.com/en-US/ATTGeneral
# url = "https://directv.wd1.myworkdayjobs.com/wday/cxs/directv/Careers/jobs"
# referal = https://directv.wd1.myworkdayjobs.com/en-US/Careers/
url = "https://target.wd5.myworkdayjobs.com/wday/cxs/target/targetcareers/jobs"
referal = "https://target.wd5.myworkdayjobs.com/targetcareers"
job_posting_json = retrieve_json(url, referal, "POST")

database = "dbname='dockerdjango' user='dbuser' host='127.0.0.1' password='dbpassword' port='5432'"
with ps.connect(database) as conn:
    with conn.cursor() as cur:
        wday_base_url = "https://target.wd5.myworkdayjobs.com/wday/cxs/target/targetcareers/job/"
        for posting in job_posting_json['jobPostings']:
            remote_text = posting.get('remoteType', False)
            if is_remote(cur, remote_text):
                print(f"Job posting is remote: {remote_text}")
                continue

            external_path = posting['externalPath']
            wday_external_url = get_last_link_part(external_path)
            wday_url = wday_base_url + wday_external_url
            referal_url = referal + "/details/" + wday_external_url
            posting_details = retrieve_json(wday_url, referal_url, "GET")

            location_text = posting_details['jobPostingInfo'].get(
                'location', False)

            if location_text:
                print(f"posting locations {posting}")
                parse_locations = parse_for_locations(location_text)
                for parse in parse_locations:
                    city, state = split_commas(parse)
                    state = state.strip()
                    state = ensure_state_full(state)
                    city = str.lower(city).strip()
                    state = str.lower(state).strip()
                    is_real_location = is_location_in_us(city, state)
                    if is_real_location:
                        print(f"location {parse} is real")
                    else:
                        print(f"location {parse} is not real")

            add_locations_text = posting_details['jobPostingInfo'].get(
                "additionalLocations", False)

            if add_locations_text:
                print(f"posting additional locations {posting}")
                for location_text in add_locations_text:
                    parse_locations = parse_for_locations(location_text)
                    for parse in parse_locations:
                        city, state = split_commas(parse)
                        state = state.strip()
                        state = ensure_state_full(state)
                        city = str.lower(city).strip()
                        state = str.lower(state).strip()
                        is_real_location = is_location_in_us(city, state)
                        if is_real_location:
                            print(f"location {parse} is real")
                        else:
                            print(f"location {parse} is not real")

            # locations_text = posting.get('locationsText', False)
            # # print(parse_for_locations(locations_text),
            # # f"locationsText: {locations_text}")
            # conn.commit()
