from types import GeneratorType
import datetime as dt
import json
import re
import requests


# create list stripped
# loop over techs
# create string strip equal to tech
# check if strip[0] is alphanumeric
# if it is assign strip to strip[1]
# check if strip[-1] is alphanumeric
# if it is assign strip to strip[-1]
# add strip to stripped
def _strip_techs(techs: list[str]):
    stripped = []
    for tech in techs:
        if not tech[0].isalpha():
            tech = tech[1:]
        if not tech[-1].isalpha():
            tech = tech[:-1]
        stripped.append(tech)
    return stripped


# get job description
# find all upper matches in job_post
# find all lower matches in job_post
# strip whitespace/combiners from all matches
# translate matches using synonym tech dict
# return set(matches)
def _retrieve_tech(
    job_post: dict,
    sensitive: re.Pattern[str],
    insensitive: re.Pattern[str],
    synonyms: dict[str, str],
    parents: dict[str, str],
) -> list[str]:
    job_description = job_post["jobPostingInfo"].get("jobDescription", None)
    if job_description is None:
        return []

    sensitive_matches = re.findall(sensitive, job_description)
    job_description = str.lower(job_description)
    insensitive_matches = re.findall(insensitive, job_description)

    # loop over sensitive_matches
    # check if tech[0] is alphanumeric
    # if it is then modify tech

    stripped_sensitive = _strip_techs(sensitive_matches)
    stripped_insensitive = _strip_techs(insensitive_matches)

    translated_sensitive = [synonyms.get(tech, tech) for tech in stripped_sensitive]
    translated_insensitive = [synonyms.get(tech, tech) for tech in stripped_insensitive]

    parents_sensitive = [
        parents.get(tech) for tech in stripped_sensitive if parents.get(tech)
    ]
    parents_insensitive = [
        parents.get(tech) for tech in stripped_insensitive if parents.get(tech)
    ]
    techs_sensitive = translated_sensitive + parents_sensitive
    techs_insensitive = translated_insensitive + parents_insensitive

    return sorted(list(set(techs_sensitive + techs_insensitive)))


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
    full_state = abrev_to_state.get(state, state)
    return full_state


# strip city, state
# ensure state full
# lower case city, state
# return True if location in location_list else False
def _is_location_in_location_list(
    location: str, location_list: list[list[str]]
) -> bool:
    city, state = str.split(location, ",")
    city, state = city.strip(), state.strip()
    state = ensure_state_full(state)
    city, state = str.lower(city), str.lower(state)

    return [city, state] in location_list


# create matches list
# if parse locations is str then make it into a list
# loop over each str and find matches
# add matches to list
def _parse_locations(texts: str | list[str]) -> list[str]:
    locations = []
    if type(texts) is str:
        texts = [texts]

    for text in texts:
        regex = re.compile(
            r"(?=((?:(?<=\b)(?:[A-Za-z.])+ ){0,3}(?<=\b)(?:[A-Za-z.])+,(?:(?: |)(?:[A-Za-z.])+){1,2}))"
        )
        matches = re.findall(regex, text)
        [locations.append(match) for match in matches]
        print(locations)
    return locations


# create locations
# parse all locations in location text
# add all locations in u.s.
# parse additional location text
# add all additional locations in u.s.
# return locations
def _retrieve_locations(job_post: dict, location_list: list[list[str]]) -> list[str]:
    locations_result = []

    location_text = job_post["jobPostingInfo"].get("location", False)
    if location_text:
        parsed_locations = _parse_locations(location_text)
        for location in parsed_locations:
            if _is_location_in_location_list(location, location_list):
                locations_result.append(location)

    add_location_text = job_post["jobPostingInfo"].get("additionalLocations", False)
    if add_location_text:
        parsed_add_locations = _parse_locations(add_location_text)
        for location in parsed_add_locations:
            if _is_location_in_location_list(location, location_list):
                locations_result.append(location)

    return locations_result


# first get the start date
# return false if date is false
# convert rate
# check if date is today
# if it is retun true
# else return false
def _is_date(job_post: dict, date: dt.date) -> bool:
    job_date = job_post["jobPostingInfo"].get("startDate", False)
    if job_date is False:
        return False

    job_date = dt.date.fromisoformat(job_date)

    if date == job_date:
        return True
    else:
        return False


def _get_tor_session() -> requests.Session:
    session = requests.session()
    session.proxies = {
        "http": "socks5://127.0.0.1:9050",
        "https": "socks5://127.0.0.1:9050",
    }
    return session


def _get_wday_base_url(url: str) -> str:
    base = url[:-1] + "/"
    return base


def _get_last_link_part(link: str) -> str:
    regex = re.compile(r"[^/]+(?=$)")
    match = re.search(regex, link)
    res = match.group(0)
    return res


# request job_summary
# loop over job summary
# get job details
# yield job details
# return details
def _request_job_post(
    url: str, offset: int, request_count: int, applied_facets: dict = {}
) -> GeneratorType:
    try:
        session = _get_tor_session()
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
        }
        payload = json.dumps(
            {
                "appliedFacets": applied_facets,
                "limit": request_count,
                "offset": offset,
                "searchText": "",
            }
        )
        job_sum_request = session.request("POST", url, headers=headers, data=payload)
        job_sum = json.loads(job_sum_request.text)
        job_sum_posts = job_sum["jobPostings"]
        for job_sum in job_sum_posts:
            job_post_url = _get_wday_base_url(url) + _get_last_link_part(
                job_sum["externalPath"]
            )
            job_post_request = session.request("GET", job_post_url, headers=headers)
            job_post = json.loads(job_post_request.text)
            yield job_post
    except Exception:
        yield None


# create ({location, stack}: count) dict
# create ({location, tech}: count) dict
# loop over uris
# loop over 20 call
# loop over job posting
# _request_job_post
# _is_date
# _is_remote
# call _retrieve_location to retrieve locations
# call _retrieve_tech to retrieve tech count and stack
# add location: stack count to list for job posting
# add location: tech count to list for job posting
# return tech and stack list
def _parse_workday(
    date: dt.date,
    urls: list[str],
    location_list: list[list[str]],
    sensitive: re.Pattern[str],
    insensitive: re.Pattern[str],
    synonyms: dict[str, str],
    parents: dict[str, str],
) -> tuple[dict[tuple[str, str], int], dict[tuple[str, str], int]]:
    tech_count = {}
    stack_count = {}
    wday_max_job_request_count = 20

    for uri in urls:
        offset = 0
        while True:
            count = 0
            for job_post in _request_job_post(uri, offset, wday_max_job_request_count):
                if job_post is None:
                    count += 1
                    print("job_post is None")
                    continue

                if _is_date(job_post, date) is False:
                    count += 1
                    continue

                locations = _retrieve_locations(job_post, location_list)
                techs = _retrieve_tech(
                    job_post, sensitive, insensitive, synonyms, parents
                )

                if techs == []:
                    count += 1
                    continue

                for location in locations:
                    for tech in techs:
                        if (location, tech) in tech_count:
                            tech_count[(location, tech)] += 1
                        else:
                            tech_count[(location, tech)] = 1

                for location in locations:
                    if (location, tuple(techs)) in stack_count:
                        stack_count[(location, tuple(techs))] += 1
                    else:
                        stack_count[(location, tuple(techs))] = 1

                count += 1

            if count != wday_max_job_request_count:
                break
            offset += wday_max_job_request_count
    return (tech_count, stack_count)
