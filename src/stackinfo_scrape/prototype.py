import requests
from stem import Signal
from stem.control import Controller
import json
import pandas as pd
import psycopg as ps
import re
import datetime as dt


def get_tor_session():
    session = requests.session()
    session.proxies = {
        "http": "socks5://127.0.0.1:9050",
        "https": "socks5://127.0.0.1:9050",
    }
    return session


def renew_connection():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password="password")
        controller.signal(Signal.NEWNYM)


def retrieve_json(url, method, payload):
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
    }
    session = get_tor_session()
    response = session.request(method, url, headers=headers, data=payload)
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
            case "y":
                cur.execute(
                    "INSERT INTO remote (remote_text, is_remote) VALUES (%s, %s);",
                    (remote_text, True),
                )
                return True
            case "n":
                cur.execute(
                    "INSERT INTO remote (remote_text, is_remote) VALUES (%s, %s);",
                    (remote_text, False),
                )
                return False


def find_location(city, state):
    states = {
        "alabama",
        "alaska",
        "american samoa",
        "arizona",
        "arkansas",
        "california",
        "colorado",
        "connecticut",
        "delaware",
        "district of columbia",
        "florida",
        "georgia",
        "guam",
        "hawaii",
        "idaho",
        "illinois",
        "indiana",
        "iowa",
        "kansas",
        "kentucky",
        "louisiana",
        "maine",
        "maryland",
        "massachusetts",
        "michigan",
        "minnesota",
        "minor outlying islands",
        "mississippi",
        "missouri",
        "montana",
        "nebraska",
        "nevada",
        "new hampshire",
        "new jersey",
        "new mexico",
        "new york",
        "north carolina",
        "north dakota",
        "northern mariana islands",
        "ohio",
        "oklahoma",
        "oregon",
        "pennsylvania",
        "puerto rico",
        "rhode island",
        "south carolina",
        "south dakota",
        "tennessee",
        "texas",
        "u.s. virgin islands",
        "utah",
        "vermont",
        "virginia",
        "washington",
        "west virginia",
        "wisconsin",
        "wyoming",
    }
    if state not in states:
        return False
    locations = pd.read_csv("./uscities.csv")
    left = 0
    right = len(locations) - 1
    while left <= right:
        point = left + (right - left) // 2
        if locations.iloc[point]["city"] == city:
            return f"{city}, {state}"
        elif locations.iloc[point]["city"] < city:
            left = point + 1
        else:
            right = point - 1
    return False


def parse_for_locations(location_text):
    regex = re.compile(
        r"(?=((?:(?<=\b)(?:[A-Za-z.])+ ){0,3}(?<=\b)(?:[A-Za-z.])+,(?:(?: |)(?:[A-Za-z.])+){1,2}))"
    )
    matches = re.findall(regex, location_text)
    return matches


def split_commas(string):
    regex = re.compile(r",")
    res = re.split(regex, string)
    return res


def ensure_state_full(state):
    abrev_to_state = {
        "AL": "Alabama",
        "AK": "Alaska",
        "AZ": "Arizona",
        "CA": "California",
        "CO": "Colorado",
        "CT": "Connecticut",
        "DE": "Delaware",
        "FL": "Florida",
        "GA": "Georgia",
        "HI": "Hawaii",
        "ID": "Idaho",
        "IL": "Illinois",
        "IN": "Indiana",
        "IA": "Iowa",
        "KS": "Kansas",
        "KY": "Kentucky",
        "LA": "Louisiana",
        "ME": "Maine",
        "MD": "Maryland",
        "MA": "Massachusetts",
        "MI": "Michigan",
        "MN": "Minnesota",
        "MS": "Mississippi",
        "MO": "Missouri",
        "MT": "Montana",
        "NE": "Nebraska",
        "NV": "Nevada",
        "NH": "New Hampshire",
        "NJ": "New Jersey",
        "NM": "New Mexico",
        "NY": "New York",
        "NC": "North Carolina",
        "ND": "North Dakota",
        "OH": "Ohio",
        "OK": "Oklahoma",
        "OR": "Oregon",
        "PA": "Pennsylvania",
        "RI": "Rhode Island",
        "SC": "South Carolina",
        "SD": "South Dakota",
        "TN": "Tennessee",
        "TX": "Texas",
        "UT": "Utah",
        "VT": "Vermont",
        "VA": "Virginia",
        "WA": "Washington",
        "WV": "West Virginia",
        "WI": "Wisconsin",
        "WY": "Wyoming",
    }
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


def determine_locations(location_text):
    locations = []
    parse_locations = parse_for_locations(location_text)
    for parse in parse_locations:
        city, state = split_commas(parse)
        state = state.strip()
        city = city.strip()
        state = ensure_state_full(state)
        city = str.lower(city)
        state = str.lower(state)
        location = find_location(city, state)
        if location:
            locations.append(location)
    return locations


def clean_up_tech(tech):
    cleaned = tech[1:]
    cleaned = cleaned[:-1]
    return cleaned


def determine_technologies(posting_text):
    upper_regex = re.compile(r"(?: |\()Go(?: |,|\))|(?: |\()REST(?: |,|\))")
    lower_regex = re.compile(
        r"(?: |\()c-sharp(?: |,|\))|(?: |\()c#(?: |,|\))|(?: |\()csharp(?: |,|\))|(?: |\()java(?: |,|\))|(?: |\()kotlin(?: |,|\))|(?: |\()python(?: |,|\))|(?: |\()springboot(?: |,|\))|(?: |\()react(?: |,|\))|(?: |\()postgresql(?: |,|\))|(?: |\()postgre(?: |,|\))|(?: |\()sql(?: |,|\))|(?: |\()kafka(?: |,|\))|(?: |\()javascript(?: |,|\))|(?: |\()typescript(?: |,|\))|(?: |\()swift(?: |,|\))|(?: |\()graphql(?: |,|\))|(?: |\()json(?: |,|\))|(?: |\()ios(?: |,|\))|(?: |\()xcodebuild(?: |,|\))|(?: |\()bash(?: |,|\))|(?: |\()cloudflare(?: |,|\))|(?: |\()pyspark(?: |,|\))|(?: |\()azure(?: |,|\))|(?: |\()aws(?: |,|\))|(?: |\()mysql(?: |,|\))|(?: |\()nosql(?: |,|\))|(?: |\()mongodb(?: |,|\))|(?: |\()snowflake(?: |,|\))|(?: |\()bigquery(?: |,|\))|(?: |\()node\.js(?: |,|\))|(?: |\()nodejs(?: |,|\))|(?: |\()linux(?: |,|\))|(?: |\()docker(?: |,|\))|(?: |\()googlecloud(?: |,|\))|(?: |\()mulesoft(?: |,|\))|(?: |\()html(?: |,|\))|(?: |\()xml(?: |,|\))|(?: |\()redis(?: |,|\))|(?: |\()splunk(?: |,|\))|(?: |\()git(?: |,|\))|(?: |\()jira(?: |,|\))|(?: |\()jenkins(?: |,|\))|(?: |\()kubernetes(?: |,|\))|(?: |\()unix(?: |,|\))(?: |\()figma(?: |,|\))(?: |\()cassandra(?: |,|\))(?: |\()vela(?: |,|\))(?: |\()influxdb(?: |,|\))(?: |\()unix(?: |,|\))(?: |\()logstash(?: |,|\))(?: |\()kibana(?: |,|\))(?: |\()rabbitmq(?: |,|\))(?: |\()ibmmq(?: |,|\))(?: |\()salesforce(?: |,|\))"
    )

    regex_to_tech = {
        "c-sharp": "c#",
        "csharp": "c#",
        "nodejs": "node.js",
        "postgre": "postgresql",
        "Go": "go",
        "golang": "go",
    }

    upper_matches = re.findall(upper_regex, posting_text)
    posting_text = str.lower(posting_text)
    lower_matches = re.findall(lower_regex, posting_text)
    result = []
    for match in lower_matches:
        tech = clean_up_tech(match)
        translate = regex_to_tech.get(tech, False)
        if translate:
            result.append(translate)
        else:
            result.append(tech)

    for match in upper_matches:
        tech = clean_up_tech(match)
        translate = regex_to_tech.get(tech, False)
        if translate:
            result.append(translate)
        else:
            result.append(tech)

    return set(result)


def retrieve_workday_details(wday_base_url, posting):
    external_path = posting["externalPath"]
    wday_external_url = get_last_link_part(external_path)
    wday_url = wday_base_url + wday_external_url
    posting_details = retrieve_json(wday_url, "GET", None)
    return posting_details


def retrieve_workday_locations(posting):
    all_locations = []
    location_text = posting["jobPostingInfo"].get("location", False)
    if location_text:
        locations = determine_locations(location_text)
        [all_locations.append(location) for location in locations]

    add_locations_text = posting["jobPostingInfo"].get("additionalLocations", False)
    if add_locations_text:
        for add_location in add_locations_text:
            add_location = determine_locations(add_location)
            [all_locations.append(location) for location in add_location]
    return all_locations


def retrieve_workday_tech(posting):
    techs = {}
    posting_text = posting["jobPostingInfo"].get("jobDescription")
    if posting_text:
        techs = determine_technologies(posting_text)
    return techs


def is_workday_date_within_range(posting_details, timedelta_range):
    start_date = posting_details["jobPostingInfo"].get("startDate", False)
    if start_date is False:
        return False

    current_date = dt.date.today()
    posting_date = dt.date.fromisoformat(start_date)

    if current_date - posting_date <= timedelta_range:
        return True
    else:
        return False


def get_wday_base_url(url):
    base = url[:-1] + "/"
    return base


# url = "https://att.wd1.myworkdayjobs.com/wday/cxs/att/ATTGeneral/jobs"
# referal = "https://att.wd1.myworkdayjobs.com/en-US/ATTGeneral"
# wday_base_url = "https://att.wd1.myworkdayjobs.com/wday/cxs/att/ATTGeneral/job/"
# url = "https://directv.wd1.myworkdayjobs.com/wday/cxs/directv/Careers/jobs"
# referal = "https://directv.wd1.myworkdayjobs.com/en-US/Careers/"
# wday_base_url = "https://directv.wd1.myworkdayjobs.com/wday/cxs/directv/Careers/job/"
# url = "https://target.wd5.myworkdayjobs.com/wday/cxs/target/targetcareers/jobs"
# referal = "https://target.wd5.myworkdayjobs.com/targetcareers"
# wday_base_url = "https://target.wd5.myworkdayjobs.com/wday/cxs/target/targetcareers/job/"


database = "dbname='dockerdjango' user='dbuser' host='127.0.0.1' password='dbpassword' port='5432'"
offset = 0
range = dt.timedelta(days=7)

with ps.connect(database) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM urls")
        urls_table = cur.fetchall()
        urls = [row[0] for row in urls_table]
        for url in urls:
            print(url)
            while True:
                payload = json.dumps(
                    {
                        "appliedFacets": {},
                        "limit": 20,
                        "offset": offset,
                        "searchText": "",
                    }
                )
                job_posting_json = retrieve_json(url, "POST", payload)
                for posting in job_posting_json["jobPostings"]:
                    posting_details = retrieve_workday_details(
                        get_wday_base_url(url), posting
                    )
                    date = posting_details["jobPostingInfo"].get("startDate", False)
                    current_date = dt.date.today()
                    posting_date = dt.date.fromisoformat(date)

                    if not is_workday_date_within_range(posting_details, range):
                        continue

                    remote_text = posting.get("remoteType", False)
                    if is_remote(cur, remote_text):
                        print(f"Job posting is remote: {remote_text}")
                        print("--------------------")
                        continue

                    all_locations = retrieve_workday_locations(posting_details)
                    techs = retrieve_workday_tech(posting_details)

                    print(techs)
                    print(all_locations)
                    print("--------------------")
                post_count = len(job_posting_json["jobPostings"])
                if post_count != 20:
                    break
                offset += 20
