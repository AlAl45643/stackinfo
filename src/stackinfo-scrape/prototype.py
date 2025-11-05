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


session = get_tor_session()
# url = "https://emcins.wd5.myworkdayjobs.com/wday/cxs/emcins/EMC_Careers/jobs"
url = "https://target.wd5.myworkdayjobs.com/wday/cxs/target/targetcareers/jobs"

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "referer": "https://target.wd5.myworkdayjobs.com/targetcareers",
}

session = get_tor_session()
response = session.request("POST", url, headers=headers)
result1 = json.loads(response.text)

# url3 = "https://att.wd1.myworkdayjobs.com/wday/cxs/att/ATTGeneral/jobs"
# headers3 = {
#     "accept": "application/json",
#     "content-type": "application/json",
#     "referer": "https://att.wd1.myworkdayjobs.com/en-US/ATTGeneral",
# }
# response3 = session.request("POST", url3, headers=headers3)
# result3 = json.loads(response3.text)

# url2 = "https://directv.wd1.myworkdayjobs.com/wday/cxs/directv/Careers/jobs"
# headers2 = {
#     "accept": "application/json",
#     "content-type": "application/json",
#     "referer": "https://directv.wd1.myworkdayjobs.com/en-US/Careers/",
# }
# response2 = session.request("POST", url2, headers=headers2)
# result2 = json.loads(response2.text)

conn = ps.connect(
    "dbname='dockerdjango' user='dbuser' host='127.0.0.1' password='dbpassword' port='5432'")
cur = conn.cursor()
locations = pd.read_csv("./uscities.csv")

for posting in result1['jobPostings']:
    remote_text = posting.get('remoteType', False)
    remote = False
    if remote_text:
        cur.execute(
            f"SELECT * FROM remote WHERE remote_text = '{remote_text}';")
        res = cur.fetchall()
        if res != []:
            remote = res[0][2]
        else:
            print(remote_text)
            inp = input("Is this remote (y or n)")
            if inp == 'y':
                cur.execute(
                    "INSERT INTO remote (remote_text, is_remote) VALUES (%s, %s);", (remote_text, True))
                remote = True
            else:
                cur.execute(
                    "INSERT INTO remote (remote_text, is_remote) VALUES (%s, %s);", (remote_text, False))
                remote = False

    if remote:
        continue

    location_text = posting.get('locationsText', False)
    if not location_text:
        continue
    regex = re.compile("[Aa]labama|[Aa]laska|[Aa]rizona|[Aa]rkansas|[Cc]alifornia|[Cc]olorado|[Cc]onnecticut|[Dd]elaware|[Ff]lorida|[Gg]eorgia|[Hh]awaii|[Ii]daho|[Ii]llinois|[Ii]ndiana|[Ii]owa|[Kk]ansas|[Kk]entucky|[Ll]ouisiana|[Mm]aine|[Mm]aryland|[Mm]assachusetts|[Mm]ichigan|[Mm]innesota|[Mm]ississippi|[Mm]issouri|[Mm]ontana|[Nn]ebraska|[Nn]evada|[Nn]ew [Hh]ampshire|[Nn]ew [Jj]ersey|[Nn]ew [Mm]exico|[Nn]ew [Yy]ork|[Nn]orth [Cc]arolina|[Nn]orth [Dd]akota|[Oo]hio|[Oo]klahoma|[Oo]regon|[Pp]ennsylvania|[Rr]hode [Ii]sland|[Ss]outh [Cc]arolina|[Ss]outh [Dd]akota|[Tt]ennessee|[Tt]exas|[Uu]tah|[Vv]ermont|[Vv]irginia|[Ww]ashington|[Ww]est [Vv]irginia|[Ww]isconsin|[Ww]yoming|AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY")
    abrev_to_state = {'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona',   'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana',
                      'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'}


    state_match = re.search(regex, location_text)

    def first_location_match(matches, location):
        for i in range(len(matches)):
            regex = re.compile(matches.iloc[i])
            res = re.search(regex, location)
            if res:
                return matches.iloc[i]

    locations = pd.read_csv("./uscities.csv")
    if state_match:
        state = state_match.group(0)
        if len(state) == 2:
            state = abrev_to_state[state]
        state = str.lower(state)
        locations = locations[locations['admin_name'] == state]
        city = first_location_match(
            locations['city'], str.lower(location_text))
        if state and city:
            print(state, city)
        else:
            print(state, "invalid", f"input: {location_text}")
    else:
        print("invalid invalid", f"input: {location_text}")


conn.commit()
cur.close()
conn.close()
