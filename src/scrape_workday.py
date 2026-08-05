from aiohttp_socks._errors import ProxyError
import asyncio
import datetime as dt
import json
import os
import re
import subprocess
import time
from collections.abc import Sequence
from json.decoder import JSONDecodeError
from typing import Literal, Pattern
import logging

import aiohttp
from aiohttp_socks import ProxyConnector


class Scrape:
    timeout = aiohttp.ClientTimeout(total=600)
    log = logging.getLogger(__name__)
    logging.basicConfig(filename=f'logs/{str(dt.date.today())}.log', encoding='utf-8', level=logging.DEBUG)

    def __init__(self, tor_sem: asyncio.Semaphore):
        self.tor_sem = tor_sem

    def _strip_techs(self, techs: list[str]) -> list[str]:
        stripped = []
        strip = {" ", ".", "(", "/", ",", ")"}
        for tech in techs:
            if tech[0] in strip:
                tech = tech[1:]
            if tech[-1] in strip:
                tech = tech[:-1]

            stripped.append(tech)
        return stripped

    def _pattern_techs(self, techs: list[str]) -> Pattern:
        res = ""
        for tech in techs:
            res += r"(?: |\(|(?<=/))" + tech + r"(?: |\.|,|(?=/)|\))"
            if tech != techs[-1]:
                res += "|"

        return re.compile(res)

    def _replace_period_techs(self, techs: list[str]) -> list[str]:
        for i in range(len(techs)):
            if "." in techs[i]:
                techs[i] = techs[i].replace(".", "\\.")
        return techs

    def _retrieve_tech(
        self,
        job_post: dict,
        sensitive: list[str],
        insensitive: list[str],
        synonyms: dict[str, str],
        parents: dict[str, str],
    ) -> list[str]:
        job_post_info = job_post.get("jobPostingInfo", False)
        if job_post_info is False:
            return []

        job_description = job_post_info.get("jobDescription", None)
        if job_description is None:
            return []

        sensitive_period = self._replace_period_techs(sensitive)
        insensitive_period = self._replace_period_techs(insensitive)

        sensitive_pattern = self._pattern_techs(sensitive_period)
        insensitive_pattern = self._pattern_techs(insensitive_period)

        sensitive_matches = re.findall(sensitive_pattern, job_description)
        job_description = str.lower(job_description)
        insensitive_matches = re.findall(insensitive_pattern, job_description)

        stripped_sensitive = self._strip_techs(sensitive_matches)
        stripped_insensitive = self._strip_techs(insensitive_matches)

        translated_sensitive = [synonyms.get(tech, tech) for tech in stripped_sensitive]
        translated_insensitive = [
            synonyms.get(tech, tech) for tech in stripped_insensitive
        ]

        parents_sensitive = []
        for tech in translated_sensitive:
            if parents.get(tech):
                parents_sensitive.append(tech)
                parents_sensitive.append(parents.get(tech))
            else:
                parents_sensitive.append(tech)

        parents_insensitive = []
        for tech in translated_insensitive:
            if parents.get(tech):
                parents_insensitive.append(tech)
                parents_insensitive.append(parents.get(tech))
            else:
                parents_insensitive.append(tech)

        res = sorted(list(set(parents_insensitive + parents_sensitive)))

        return res

    def ensure_state_full(self, state) -> str:
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

    def _is_location_in_location_list(
        self, location: str, location_list: Sequence[tuple[str, str]]
    ) -> tuple[str, str] | Literal[False]:
        city, state = str.split(location, ",")
        city, state = city.strip(), state.strip()
        state = self.ensure_state_full(state)
        city, state = str.lower(city), str.lower(state)

        return (city, state) if (city, state) in location_list else False

    def _parse_locations(self, texts: str | list[str]) -> list[str]:
        locations = []
        if type(texts) is str:
            texts = [texts]

        for text in texts:
            regex = re.compile(
                r"(?=((?:(?<=\b)(?:[A-Za-z.])+ ){0,3}(?<=\b)(?:[A-Za-z.])+,(?:(?: |)(?:[A-Za-z.])+){1,2}))"
            )
            matches = re.findall(regex, text)
            [locations.append(match) for match in matches]
        return locations

    def _retrieve_locations(
        self, job_post: dict, location_list: Sequence[tuple[str, str]]
    ) -> list[str]:
        locations_result = []

        job_post_info = job_post.get("jobPostingInfo", False)
        if job_post_info is False:
            return []

        location_text = job_post_info.get("location", False)
        if location_text:
            parsed_locations = self._parse_locations(location_text)
            for location in parsed_locations:
                stand_location = self._is_location_in_location_list(
                    location, location_list
                )
                if stand_location:
                    locations_result.append(stand_location)

        add_location_text = job_post_info.get("additionalLocations", False)
        if add_location_text:
            parsed_add_locations = self._parse_locations(add_location_text)
            for location in parsed_add_locations:
                stand_location = self._is_location_in_location_list(
                    location, location_list
                )
                if stand_location:
                    locations_result.append(stand_location)

        return locations_result

    def _is_date(self, job_post: dict, date: dt.date) -> bool:
        job_post_info = job_post.get("jobPostingInfo", False)
        if job_post_info is False:
            return False

        job_date = job_post_info.get("startDate", False)
        if job_date is False:
            return False

        job_date = dt.date.fromisoformat(job_date)

        if date == job_date:
            return True
        else:
            return False

    def _get_tor_session(self) -> aiohttp.ClientSession:
        connector = ProxyConnector.from_url("socks5://127.0.0.1:9050")
        session = aiohttp.ClientSession(connector=connector, timeout=self.timeout)
        return session

    def _get_wday_base_url(self, url: str) -> str:
        base = url[:-1] + "/"
        return base

    def _get_last_link_part(self, link: str) -> str:
        regex = re.compile(r"[^/]+(?=$)")
        match = re.search(regex, link)
        res = ""
        if match:
            res = match.group(0)
        return res

    async def _request_job_count(self, url: str, applied_facets: dict = {}) -> int:
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
        }
        payload = json.dumps(
            {
                "appliedFacets": applied_facets,
                "limit": 20,
                "offset": 0,
                "searchText": "",
            }
        )
        try:
            async with self.tor_sem:
                async with self._get_tor_session() as session:
                    async with session.post(
                        url, headers=headers, data=payload
                    ) as job_sum_request:
                        job_sum_text = await job_sum_request.text()
                        try:
                            job_sum = json.loads(job_sum_text)
                        except JSONDecodeError:
                            return 0

                        job_count = job_sum.get("total", 0)
                        return job_count
        except Exception as e:
            self.log.error(str(e))
            return 0

    async def _request_job_details(
        self, url: str, job_sum_post: dict, headers: dict
    ) -> dict | None:
        external_path = job_sum_post.get("externalPath", None)
        if external_path is None:
            return None
        job_post_url = self._get_wday_base_url(url) + self._get_last_link_part(
            external_path
        )
        async with self._get_tor_session() as session:
            try:
                async with session.get(
                    job_post_url, headers=headers
                ) as job_post_request:
                    job_post_text = await job_post_request.text()
                    try:
                        job_post = json.loads(job_post_text)
                    except JSONDecodeError:
                        return None

                    return job_post
            except ProxyError as e:
                self.log.error(str(e))
                return None

    async def _request_job_posts(
        self,
        url: str,
        offset: int,
        request_count: int,
        applied_facets: dict = {},
    ) -> list[dict]:
        job_details = []
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
        try:
            async with self.tor_sem:
                async with self._get_tor_session() as session:
                    async with session.post(
                        url, headers=headers, data=payload
                    ) as job_sum_request:
                        job_sum_text = await job_sum_request.text()
                        try:
                            job_sum = json.loads(job_sum_text)
                        except JSONDecodeError:
                            return job_details

                        if type(job_sum) is not dict:
                            return job_details
                        job_sum_posts = job_sum.get("jobPostings", None)
                        if job_sum_posts is None:
                            return job_details

                        job_post_tasks = []
                        for job_sum_post in job_sum_posts:
                            task = asyncio.create_task(
                                self._request_job_details(url, job_sum_post, headers)
                            )
                            job_post_tasks.append(task)
                        for post_task in job_post_tasks:
                            post_details = await post_task
                            job_details.append(post_details)
        except Exception as e:
            self.log.error(str(e))
            return job_details
        return job_details

    async def parse_workday(
        self,
        date: dt.date | None,
        urls: Sequence[str],
        location_list: Sequence[tuple[str, str]],
        sensitive: list[str],
        insensitive: list[str],
        synonyms: dict[str, str],
        parents: dict[str, str],
    ) -> tuple[
        dict[tuple[tuple[str, str], str], int],
        dict[tuple[tuple[str, str], tuple[str]], int],
    ]:
        self.log.info('started scrape_workday.py')
        tech_count = {}
        stack_count = {}
        wday_max_job_request_count = 20
        job_post_tasks = []
        job_count_tasks = []
        self.log.info('creating tor process')
        tor = subprocess.Popen(
            "tor",
            stdout=open("torstdout", "w+"),
            stderr=open("torstderr", "w+"),
            stdin=open("torstdin", "w+"),
            preexec_fn=os.setpgrp,
            close_fds=True,
        )
        time.sleep(10)

        try:
            self.log.info('creating _request_job_count tasks')
            for uri in urls:
                task = asyncio.create_task(self._request_job_count(uri))
                job_count_tasks.append((uri, task))

            self.log.info('processing job_count_tasks tasks')
            for uri, task in job_count_tasks:
                count = await task
                for offset in range(0, count, wday_max_job_request_count):
                    job_post_task = asyncio.create_task(
                        self._request_job_posts(uri, offset, wday_max_job_request_count)
                    )
                    job_post_tasks.append(job_post_task)

            self.log.info('processing job_posts_tasks tasks')
            for task in job_post_tasks:
                job_posts = await task
                for job_post in job_posts:
                    count += 1
                    if job_post is None:
                        continue
                    if date is not None and self._is_date(job_post, date) is False:
                        continue

                    self.log.info(f'{job_post}')
                    locations = self._retrieve_locations(job_post, location_list)
                    self.log.info(f'{locations}')
                    techs = self._retrieve_tech(
                        job_post, sensitive, insensitive, synonyms, parents
                    )
                    self.log.info(f'{techs}')
                    if techs == []:
                        continue
                    for location in locations:
                        for tech in techs:
                            if (location, tech) in tech_count:
                                tech_count[(location, tech)] += 1
                            else:
                                tech_count[(location, tech)] = 1
                    for location in locations:
                        if (location, tuple(sorted(techs))) in stack_count:
                            stack_count[(location, tuple(sorted(techs)))] += 1
                        else:
                            stack_count[(location, tuple(sorted(techs)))] = 1

        finally:
            self.log.info('killing tor')
            tor.kill()

        self.log.info('finished scraping workday jobs')
        return (tech_count, stack_count)
