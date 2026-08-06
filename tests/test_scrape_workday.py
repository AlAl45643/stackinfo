import asyncio
import json
import os
import pytest
import subprocess
import time
from src.scrape_workday import Scrape


@pytest.fixture()
def run_tor():
    tor = subprocess.Popen(
        "tor",
        stdout=open(os.devnull),
        stderr=open(os.devnull),
        stdin=open(os.devnull),
        preexec_fn=os.setpgrp,
        close_fds=True,
    )
    time.sleep(10)
    yield
    tor.kill()


def test_retrieving_techs():
    """Test the parsing of techs on a workday response."""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    response_file = open(f"{dir_path}/resources/workday_jobs_response", "r+")
    response = json.load(response_file)
    location_list_file = open(f"{dir_path}/resources/location_list", "r+")
    location_list = json.load(location_list_file)
    location_list = [(i[0], i[1]) for i in location_list]
    tech_count = {}
    stack_count = {}
    sensitive = ["SAFe"]
    insensitive = [
        "dast",
        "burp suite",
        "ibm appscan",
        "hcl appscan",
        "netsparker",
        "acunetix",
        "java",
        "python",
        "bash",
        "php",
        "javascript",
        "power bi",
        "sql",
        "excel",
        "powerpoint",
        "jira align",
        "jira cloud",
        "git",
        "servicenow",
        "react js",
        "graph ql",
        "node js",
        "mulesoft",
        "co-pilot",
        "dynatrace",
        "quantum metrics",
        "splunk",
        "next.js",
        "node.js",
        "react.js",
        "copilots",
        "no sql",
        "next js",
        "typescript",
        "bootstrap.js",
        "html5",
        "xml",
        "css3",
        "nosql",
        "cassandra",
        "mongodb",
        "mongo db",
        "spring boot",
        "kafka",
        "redis",
        "azure",
        "aws",
        "prometheus",
        "jira",
        "jenkins",
        "docker",
        "grafana",
        "kubernetes",
    ]
    synonyms = {
        "node js": "node.js",
        "react js": "react.js",
        "copilots": "co-pilot",
        "next js": "next.js",
        "no sql": "nosql",
        "mongo db": "mongodb",
    }
    parents = {"jira align": "jira", "jira cloud": "jira"}
    scrape = Scrape(asyncio.Semaphore(3))

    for job_post in response:
        locations = scrape._retrieve_locations(job_post, location_list)
        techs = scrape._retrieve_tech(
            job_post, sensitive, insensitive, synonyms, parents
        )

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

    tech_count_assert = {
        (("dallas", "texas"), "dast"): 1,
        (("bedminster", "new jersey"), "dast"): 1,
        (("middletown", "new jersey"), "dast"): 1,
        (("bothell", "washington"), "dast"): 1,
        (("alpharetta", "georgia"), "dast"): 1,
        (("atlanta", "georgia"), "dast"): 1,
        (("dallas", "texas"), "burp suite"): 1,
        (("bedminster", "new jersey"), "burp suite"): 1,
        (("middletown", "new jersey"), "burp suite"): 1,
        (("bothell", "washington"), "burp suite"): 1,
        (("alpharetta", "georgia"), "burp suite"): 1,
        (("atlanta", "georgia"), "burp suite"): 1,
        (("dallas", "texas"), "ibm appscan"): 1,
        (("bedminster", "new jersey"), "ibm appscan"): 1,
        (("middletown", "new jersey"), "ibm appscan"): 1,
        (("bothell", "washington"), "ibm appscan"): 1,
        (("alpharetta", "georgia"), "ibm appscan"): 1,
        (("atlanta", "georgia"), "ibm appscan"): 1,
        (("dallas", "texas"), "hcl appscan"): 1,
        (("bedminster", "new jersey"), "hcl appscan"): 1,
        (("middletown", "new jersey"), "hcl appscan"): 1,
        (("bothell", "washington"), "hcl appscan"): 1,
        (("alpharetta", "georgia"), "hcl appscan"): 1,
        (("atlanta", "georgia"), "hcl appscan"): 1,
        (("dallas", "texas"), "netsparker"): 1,
        (("bedminster", "new jersey"), "netsparker"): 1,
        (("middletown", "new jersey"), "netsparker"): 1,
        (("bothell", "washington"), "netsparker"): 1,
        (("alpharetta", "georgia"), "netsparker"): 1,
        (("atlanta", "georgia"), "netsparker"): 1,
        (("dallas", "texas"), "acunetix"): 1,
        (("bedminster", "new jersey"), "acunetix"): 1,
        (("middletown", "new jersey"), "acunetix"): 1,
        (("bothell", "washington"), "acunetix"): 1,
        (("alpharetta", "georgia"), "acunetix"): 1,
        (("atlanta", "georgia"), "acunetix"): 1,
        (("dallas", "texas"), "java"): 1,
        (("bedminster", "new jersey"), "java"): 1,
        (("middletown", "new jersey"), "java"): 1,
        (("bothell", "washington"), "java"): 1,
        (("alpharetta", "georgia"), "java"): 1,
        (("atlanta", "georgia"), "java"): 1,
        (("dallas", "texas"), "python"): 1,
        (("bedminster", "new jersey"), "python"): 2,
        (("bothell", "washington"), "python"): 1,
        (("alpharetta", "georgia"), "python"): 2,
        (("atlanta", "georgia"), "python"): 2,
        (("dallas", "texas"), "bash"): 1,
        (("bedminster", "new jersey"), "bash"): 1,
        (("middletown", "new jersey"), "bash"): 1,
        (("bothell", "washington"), "bash"): 1,
        (("alpharetta", "georgia"), "bash"): 1,
        (("atlanta", "georgia"), "bash"): 1,
        (("dallas", "texas"), "php"): 1,
        (("bedminster", "new jersey"), "php"): 1,
        (("middletown", "new jersey"), "php"): 1,
        (("bothell", "washington"), "php"): 1,
        (("alpharetta", "georgia"), "php"): 1,
        (("atlanta", "georgia"), "php"): 1,
        (("dallas", "texas"), "javascript"): 1,
        (("bedminster", "new jersey"), "javascript"): 1,
        (("middletown", "new jersey"), "javascript"): 1,
        (("bothell", "washington"), "javascript"): 1,
        (("alpharetta", "georgia"), "javascript"): 1,
        (("atlanta", "georgia"), "javascript"): 1,
        (("middletown", "new jersey"), "SAFe"): 1,
        (("plano", "texas"), "SAFe"): 1,
        (("alpharetta", "georgia"), "SAFe"): 1,
        (("atlanta", "georgia"), "SAFe"): 1,
        (("bedminster", "new jersey"), "SAFe"): 1,
        (("middletown", "new jersey"), "power bi"): 1,
        (("plano", "texas"), "power bi"): 1,
        (("alpharetta", "georgia"), "power bi"): 1,
        (("bedminster", "new jersey"), "power bi"): 1,
        (("middletown", "new jersey"), "python"): 2,
        (("plano", "texas"), "python"): 1,
        (("middletown", "new jersey"), "sql"): 1,
        (("plano", "texas"), "sql"): 1,
        (("alpharetta", "georgia"), "sql"): 1,
        (("atlanta", "georgia"), "sql"): 1,
        (("bedminster", "new jersey"), "sql"): 1,
        (("middletown", "new jersey"), "jira cloud"): 1,
        (("plano", "texas"), "jira cloud"): 1,
        (("alpharetta", "georgia"), "jira cloud"): 1,
        (("atlanta", "georgia"), "jira cloud"): 1,
        (("bedminster", "new jersey"), "jira cloud"): 1,
        (("middletown", "new jersey"), "git"): 1,
        (("plano", "texas"), "git"): 2,
        (("alpharetta", "georgia"), "git"): 1,
        (("atlanta", "georgia"), "git"): 1,
        (("bedminster", "new jersey"), "git"): 1,
        (("middletown", "new jersey"), "servicenow"): 1,
        (("plano", "texas"), "servicenow"): 1,
        (("alpharetta", "georgia"), "servicenow"): 1,
        (("atlanta", "georgia"), "servicenow"): 1,
        (("bedminster", "new jersey"), "servicenow"): 1,
        (("plano", "texas"), "react.js"): 1,
        (("plano", "texas"), "java"): 1,
        (("plano", "texas"), "graph ql"): 1,
        (("plano", "texas"), "node.js"): 1,
        (("plano", "texas"), "mulesoft"): 1,
        (("plano", "texas"), "co-pilot"): 1,
        (("plano", "texas"), "dynatrace"): 1,
        (("plano", "texas"), "quantum metrics"): 1,
        (("plano", "texas"), "splunk"): 1,
        (("plano", "texas"), "nosql"): 1,
        (("plano", "texas"), "next.js"): 1,
        (("plano", "texas"), "typescript"): 1,
        (("plano", "texas"), "html5"): 1,
        (("plano", "texas"), "xml"): 1,
        (("plano", "texas"), "css3"): 1,
        (("plano", "texas"), "javascript"): 1,
        (("plano", "texas"), "grafana"): 1,
        (("plano", "texas"), "prometheus"): 1,
        (("plano", "texas"), "jira"): 2,
        (("plano", "texas"), "jenkins"): 1,
        (("plano", "texas"), "docker"): 1,
        (("plano", "texas"), "kubernetes"): 1,
        (("plano", "texas"), "aws"): 1,
        (("plano", "texas"), "azure"): 1,
        (("plano", "texas"), "cassandra"): 1,
        (("plano", "texas"), "redis"): 1,
        (("plano", "texas"), "spring boot"): 1,
        (("plano", "texas"), "kafka"): 1,
        (("alpharetta", "georgia"), "excel"): 1,
        (("alpharetta", "georgia"), "jira"): 1,
        (("alpharetta", "georgia"), "powerpoint"): 1,
        (("atlanta", "georgia"), "excel"): 1,
        (("atlanta", "georgia"), "jira"): 1,
        (("atlanta", "georgia"), "power bi"): 1,
        (("atlanta", "georgia"), "powerpoint"): 1,
        (("middletown", "new jersey"), "excel"): 1,
        (("middletown", "new jersey"), "jira"): 1,
        (("middletown", "new jersey"), "powerpoint"): 1,
        (("plano", "texas"), "excel"): 1,
        (("plano", "texas"), "powerpoint"): 1,
        (("bedminster", "new jersey"), "excel"): 1,
        (("bedminster", "new jersey"), "jira"): 1,
        (("bedminster", "new jersey"), "powerpoint"): 1,
        (("plano", "texas"), "mongodb"): 1,
    }
    stack_count_assert = {
        (
            ("dallas", "texas"),
            tuple(
                sorted(
                    [
                        "dast",
                        "burp suite",
                        "ibm appscan",
                        "hcl appscan",
                        "netsparker",
                        "acunetix",
                        "java",
                        "python",
                        "bash",
                        "php",
                        "javascript",
                    ]
                )
            ),
        ): 1,
        (
            ("bedminster", "new jersey"),
            tuple(
                sorted(
                    [
                        "dast",
                        "burp suite",
                        "ibm appscan",
                        "hcl appscan",
                        "netsparker",
                        "acunetix",
                        "java",
                        "python",
                        "bash",
                        "php",
                        "javascript",
                    ]
                )
            ),
        ): 1,
        (
            ("middletown", "new jersey"),
            tuple(
                sorted(
                    [
                        "dast",
                        "burp suite",
                        "ibm appscan",
                        "hcl appscan",
                        "netsparker",
                        "acunetix",
                        "java",
                        "python",
                        "bash",
                        "php",
                        "javascript",
                    ]
                )
            ),
        ): 1,
        (
            ("bothell", "washington"),
            tuple(
                sorted(
                    [
                        "dast",
                        "burp suite",
                        "ibm appscan",
                        "hcl appscan",
                        "netsparker",
                        "acunetix",
                        "java",
                        "python",
                        "bash",
                        "php",
                        "javascript",
                    ]
                )
            ),
        ): 1,
        (
            ("alpharetta", "georgia"),
            tuple(
                sorted(
                    [
                        "dast",
                        "burp suite",
                        "ibm appscan",
                        "hcl appscan",
                        "netsparker",
                        "acunetix",
                        "java",
                        "python",
                        "bash",
                        "php",
                        "javascript",
                    ]
                )
            ),
        ): 1,
        (
            ("atlanta", "georgia"),
            tuple(
                sorted(
                    [
                        "dast",
                        "burp suite",
                        "ibm appscan",
                        "hcl appscan",
                        "netsparker",
                        "acunetix",
                        "java",
                        "python",
                        "bash",
                        "php",
                        "javascript",
                    ]
                )
            ),
        ): 1,
        (
            ("middletown", "new jersey"),
            tuple(
                sorted(
                    [
                        "SAFe",
                        "power bi",
                        "python",
                        "sql",
                        "servicenow",
                        "excel",
                        "powerpoint",
                        "jira cloud",
                        "git",
                        "jira",
                    ]
                )
            ),
        ): 1,
        (
            ("plano", "texas"),
            tuple(
                sorted(
                    [
                        "SAFe",
                        "power bi",
                        "python",
                        "sql",
                        "servicenow",
                        "excel",
                        "powerpoint",
                        "jira cloud",
                        "git",
                        "jira",
                    ]
                )
            ),
        ): 1,
        (
            ("alpharetta", "georgia"),
            tuple(
                sorted(
                    [
                        "SAFe",
                        "power bi",
                        "jira cloud",
                        "python",
                        "sql",
                        "servicenow",
                        "excel",
                        "powerpoint",
                        "git",
                        "jira",
                    ]
                )
            ),
        ): 1,
        (
            ("atlanta", "georgia"),
            tuple(
                sorted(
                    [
                        "SAFe",
                        "power bi",
                        "python",
                        "sql",
                        "servicenow",
                        "excel",
                        "powerpoint",
                        "jira cloud",
                        "git",
                        "jira",
                    ]
                )
            ),
        ): 1,
        (
            ("bedminster", "new jersey"),
            tuple(
                sorted(
                    [
                        "SAFe",
                        "power bi",
                        "python",
                        "sql",
                        "servicenow",
                        "excel",
                        "powerpoint",
                        "git",
                        "jira cloud",
                        "jira",
                    ]
                )
            ),
        ): 1,
        (
            ("plano", "texas"),
            tuple(
                sorted(
                    [
                        "aws",
                        "kubernetes",
                        "react.js",
                        "java",
                        "javascript",
                        "graph ql",
                        "node.js",
                        "mulesoft",
                        "dynatrace",
                        "quantum metrics",
                        "splunk",
                        "co-pilot",
                        "next.js",
                        "nosql",
                        "html5",
                        "xml",
                        "css3",
                        "cassandra",
                        "mongodb",
                        "spring boot",
                        "kafka",
                        "redis",
                        "azure",
                        "typescript",
                        "prometheus",
                        "grafana",
                        "git",
                        "jira",
                        "jenkins",
                        "docker",
                    ]
                )
            ),
        ): 1,
    }

    assert tech_count == tech_count_assert
    assert stack_count == stack_count_assert


@pytest.mark.asyncio
async def test_requesting_workday_payload(run_tor):
    """Test requesting many workday payloads."""
    urls = [
        "https://roche.wd3.myworkdayjobs.com/wday/cxs/roche/roche-ext/jobs",
        "https://pfizer.wd1.myworkdayjobs.com/wday/cxs/pfizer/pfizercareers/jobs",
        "https://adobe.wd5.myworkdayjobs.com/wday/cxs/adobe/external_experienced/jobs",
        "https://td.wd3.myworkdayjobs.com/wday/cxs/td/TD_Bank_Careers/jobs",
        "https://rochester.wd5.myworkdayjobs.com/wday/cxs/rochester/UR_Staff/jobs",
        "https://wexinc.wd5.myworkdayjobs.com/wday/cxs/wexinc/WEXInc/jobs",
        "https://hp.wd5.myworkdayjobs.com/wday/cxs/hp/ExternalCareerSite/jobs",
        "https://lvhn.wd1.myworkdayjobs.com/wday/cxs/lvhn/LVHN/jobs",
        "https://amfam.wd1.myworkdayjobs.com/wday/cxs/amfam/Careers/jobs",
        "https://dupont.wd5.myworkdayjobs.com/wday/cxs/dupont/Jobs/jobs",
        "https://redrobin.wd1.myworkdayjobs.com/wday/cxs/redrobin/RedRobin_Careers/jobs",
        "https://sonyglobal.wd1.myworkdayjobs.com/wday/cxs/sonyglobal/SonyGlobalCareers/jobs",
        "https://baltimorecity.wd1.myworkdayjobs.com/wday/cxs/baltimorecity/External/jobs",
        "https://cox.wd1.myworkdayjobs.com/wday/cxs/cox/Cox_External_Career_Site_1/jobs",
        "https://rockwellautomation.wd1.myworkdayjobs.com/wday/cxs/rockwellautomation/External_Rockwell_Automation/jobs",
        "https://dowjones.wd1.myworkdayjobs.com/wday/cxs/dowjones/Dow_Jones_Career/jobs",
        "https://huntingtonhospital.wd5.myworkdayjobs.com/wday/cxs/huntingtonhospital/HuntingtonHospitalCareers/jobs",
        "https://fmc.wd12.myworkdayjobs.com/wday/cxs/fmc/FMC/jobs",
        "https://hancockwhitney.wd5.myworkdayjobs.com/wday/cxs/hancockwhitney/Careers/jobs",
        "https://fmr.wd1.myworkdayjobs.com/wday/cxs/fmr/fidelitycareers/jobs",
        "https://cigna.wd5.myworkdayjobs.com/wday/cxs/cigna/cignacareers/jobs",
        "https://davita.wd1.myworkdayjobs.com/wday/cxs/davita/DKC_External/jobs",
        "https://ncratleos.wd1.myworkdayjobs.com/wday/cxs/ncratleos/ext_atleos_us/jobs",
        "https://nus.wd1.myworkdayjobs.com/wday/cxs/nus/Careers/jobs",
        "https://takeda.wd3.myworkdayjobs.com/wday/cxs/takeda/External/jobs",
        "https://db.wd3.myworkdayjobs.com/wday/cxs/db/DBWebsite/jobs",
        "https://yeticoolers.wd5.myworkdayjobs.com/wday/cxs/yeticoolers/YETI/jobs",
        "https://jda.wd5.myworkdayjobs.com/wday/cxs/jda/JDA_Careers/jobs",
        "https://ferguson.wd1.myworkdayjobs.com/wday/cxs/ferguson/Ferguson_Experienced/jobs",
        "https://rocket.wd5.myworkdayjobs.com/wday/cxs/rocket/rocket_careers/jobs",
        "https://acehardware.wd1.myworkdayjobs.com/wday/cxs/acehardware/external/jobs",
        "https://nshe.wd1.myworkdayjobs.com/wday/cxs/nshe/UNR-external/jobs",
        "https://goodyear.wd1.myworkdayjobs.com/wday/cxs/goodyear/GoodyearCareers/jobs",
        "https://tti.wd1.myworkdayjobs.com/wday/cxs/tti/TeamTTI-Jobs/jobs",
        "https://onehealthineers.wd3.myworkdayjobs.com/wday/cxs/onehealthineers/SHSJB/jobs",
        "https://ngc.wd1.myworkdayjobs.com/wday/cxs/ngc/Northrop_Grumman_External_Site/jobs",
        "https://thehartford.wd5.myworkdayjobs.com/wday/cxs/thehartford/Careers_Restricted/jobs",
        "https://comcast.wd5.myworkdayjobs.com/wday/cxs/comcast/Comcast_Careers/jobs",
        "https://shakeshack.wd5.myworkdayjobs.com/wday/cxs/shakeshack/External/jobs",
        "https://papajohns.wd1.myworkdayjobs.com/wday/cxs/papajohns/PapaJohnsCareers/jobs",
        "https://hcmportal.wd5.myworkdayjobs.com/wday/cxs/hcmportal/Search/jobs",
    ]
    offset = 0
    request_count = 20
    tasks = []
    scrape = Scrape(asyncio.Semaphore(3))
    for uri in urls:
        task = asyncio.create_task(
            scrape._request_job_posts(uri, offset, request_count), name=uri
        )
        tasks.append(task)

    for task in tasks:
        job_posts = await task
        print(task)
        assert job_posts != []


# count = 0
# job_post_tasks = 0
# create _request_job_count task
# await task
# for offset in range(0, count, wday_max_job_request_count)
#  create request_job_posts task
#  add request_job_posts task to job_post_tasks
# for task in job_post_tasks
#  await task
#  count += len(task)
async def count_job_posts(url: str) -> int:
    count = 0
    job_post_tasks = []
    scrape = Scrape(asyncio.Semaphore(3))

    job_count_task = asyncio.create_task(
        scrape._request_job_count(
            url,
        )
    )
    job_count = await job_count_task

    for offset in range(0, job_count, 20):
        task = asyncio.create_task(
            scrape._request_job_posts(
                url,
                offset,
                20,
            )
        )
        job_post_tasks.append(task)

    for task in job_post_tasks:
        res = await task
        count += len(res)

    return count


# create urls list with multiple workday urls
# create list of tasks to retrieve each urls number of jobs
# create list of tasks to count number of workday job post
# assert that the number of jobs to number of retrieved posts is equal
# @pytest.mark.asyncio
# async def test_number_of_jobs_retrieved(run_tor):
#     """Test if number of jobs retrieved is equal to number of jobs advertised."""
#     url = "https://walmart.wd5.myworkdayjobs.com/wday/cxs/walmart/WalmartExternal/jobs"
#     scrape = Scrape(asyncio.Semaphore(3))
#     num_listed_task = asyncio.create_task(
#         scrape._request_job_count(
#             url,
#         )
#     )
#     count_task = asyncio.create_task(count_job_posts(url))

#     listed_num = await num_listed_task
#     counted_num = await count_task

#     assert listed_num == counted_num


# date = today
# urls = target
# location_list = a few locations
# sensitive = a few techs
# insensitive = a few techs
# synonyms = none
# parents = none
# assert not none
@pytest.mark.asyncio
async def test_parse_workday():
    """Test if parse_workday function retrieves stack and tech count from ATT."""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    date = None
    urls = ["https://att.wd1.myworkdayjobs.com/wday/cxs/att/ATTGeneral/jobs"]
    location_list_file = open(
        os.path.join(dir_path, "resources", "location_list"), "r+"
    )
    location_list = json.load(location_list_file)
    location_list = [(i[0], i[1]) for i in location_list]
    sensitive = ["SAFe"]
    insensitive = [
        "dast",
        "burp suite",
        "ibm appscan",
        "hcl appscan",
        "netsparker",
        "acunetix",
        "java",
        "python",
        "bash",
        "php",
        "javascript",
        "power bi",
        "sql",
        "excel",
        "powerpoint",
        "jira align",
        "jira cloud",
        "git",
        "servicenow",
        "react js",
        "graph ql",
        "node js",
        "mulesoft",
        "co-pilot",
        "dynatrace",
        "quantum metrics",
        "splunk",
        "next.js",
        "node.js",
        "react.js",
        "copilots",
        "no sql",
        "next js",
        "typescript",
        "bootstrap.js",
        "html5",
        "xml",
        "css3",
        "nosql",
        "cassandra",
        "mongodb",
        "mongodb",
        "spring boot",
        "kafka",
        "redis",
        "azure",
        "aws",
        "prometheus",
        "jira",
        "jenkins",
        "docker",
        "grafana",
        "kubernetes",
    ]

    synonyms = {
        "node js": "node.js",
        "react js": "react.js",
        "copilots": "co-pilot",
        "next js": "next.js",
        "no sql": "nosql",
        "mongo db": "mongodb",
    }
    parents = {"jira align": "jira", "jira cloud": "jira"}
    scrape = Scrape(asyncio.Semaphore(3))

    res = await scrape.parse_workday(
        date, urls, location_list, sensitive, insensitive, synonyms, parents
    )
    assert res[0] != {} and res[1] != {}


def test_retrieve_tech():
    scrape = Scrape(asyncio.Semaphore(3))
    res = scrape._retrieve_tech(
        {"jobPostingInfo": {"jobDescription": " sql "}}, ["R"], ["sql"], {}, {}
    )
    assert res == ["sql"]


def test_retrieve_tech_dot():
    scrape = Scrape(asyncio.Semaphore(3))
    res = scrape._retrieve_tech(
        {"jobPostingInfo": {"jobDescription": " .net "}}, ["R"], [".net"], {}, {}
    )
    assert res == [".net"]


def test_retrieve_tech_edges():
    scrape = Scrape(asyncio.Semaphore(3))
    res = scrape._retrieve_tech(
        {
            "jobPostingInfo": {
                "jobDescription": " sql. python, (c#, .net/postgresql/fastapi)"
            }
        },
        ["R"],
        ["sql", ".net", "c#", "python", "postgresql", "fastapi"],
        {},
        {},
    )
    assert sorted(res) == sorted(
        ["sql", ".net", "c#", "python", "postgresql", "fastapi"]
    )


def test_retrieve_tech_synonyms():
    scrape = Scrape(asyncio.Semaphore(3))
    res = scrape._retrieve_tech(
        {"jobPostingInfo": {"jobDescription": " csharp "}},
        ["R"],
        ["c#", "csharp"],
        {"csharp": "c#"},
        {},
    )
    assert res == ["c#"]


def test_retrieve_tech_parent():
    scrape = Scrape(asyncio.Semaphore(3))
    res = scrape._retrieve_tech(
        {"jobPostingInfo": {"jobDescription": " postgresql "}},
        ["R"],
        ["postgresql", "sql"],
        {},
        {"postgresql": "sql"},
    )
    assert res == ["postgresql", "sql"]
