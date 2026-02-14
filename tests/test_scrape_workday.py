import asyncio
import json
import os
import re
import pytest
from src.scrape_workday import (
    _request_job_posts,
    _retrieve_locations,
    _retrieve_tech,
    parse_workday,
    _request_job_count,
)


def test_retrieving_techs():
    """Test the parsing of techs on a workday response."""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    response_file = open(f"{dir_path}/resources/workday_jobs_response", "r+")
    response = json.load(response_file)
    location_list_file = open(f"{dir_path}/resources/location_list", "r+")
    location_list = json.load(location_list_file)
    tech_count = {}
    stack_count = {}
    sensitive = re.compile(r"(?: |>|\.|\(|(?<=/))SAFe(?: |>|\.|,|(?=/)|\))")
    insensitive = re.compile(
        r"(?: |>|\.|\(|(?<=/))dast(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))burp suite(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))ibm appscan(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))hcl appscan(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))netsparker(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))acunetix(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))java(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))python(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))bash(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))php(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))javascript(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))power bi(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))sql(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))excel(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))powerpoint(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))jira align(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))jira cloud(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))git(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))servicenow(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))react js(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))graph ql(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))node js(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))mulesoft(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))co-pilot(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))dynatrace(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))quantum metrics(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))splunk(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))next.js(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))node.js(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))react.js(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))copilots(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))no sql(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))next js(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))typescript(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))bootstrap.js(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))html5(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))xml(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))css3(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))nosql(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))cassandra(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))mongodb(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))mongo db(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))spring boot(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))kafka(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))redis(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))azure(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))aws(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))prometheus(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))jira(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))jenkins(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))docker(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))grafana(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))kubernetes(?: |>|\.|,|(?=/)|\))"
    )
    synonyms = {
        "node js": "node.js",
        "react js": "react.js",
        "copilots": "co-pilot",
        "next js": "next.js",
        "no sql": "nosql",
        "mongo db": "mongodb",
    }
    parents = {"jira align": "jira", "jira cloud": "jira"}

    for job_post in response:
        locations = _retrieve_locations(job_post, location_list)
        techs = _retrieve_tech(job_post, sensitive, insensitive, synonyms, parents)

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
        ("Dallas, Texas", "dast"): 1,
        ("Bedminster, New Jersey", "dast"): 1,
        ("Middletown, New Jersey", "dast"): 1,
        ("Bothell, Washington", "dast"): 1,
        ("Alpharetta, Georgia", "dast"): 1,
        ("Atlanta, Georgia", "dast"): 1,
        ("Dallas, Texas", "burp suite"): 1,
        ("Bedminster, New Jersey", "burp suite"): 1,
        ("Middletown, New Jersey", "burp suite"): 1,
        ("Bothell, Washington", "burp suite"): 1,
        ("Alpharetta, Georgia", "burp suite"): 1,
        ("Atlanta, Georgia", "burp suite"): 1,
        ("Dallas, Texas", "ibm appscan"): 1,
        ("Bedminster, New Jersey", "ibm appscan"): 1,
        ("Middletown, New Jersey", "ibm appscan"): 1,
        ("Bothell, Washington", "ibm appscan"): 1,
        ("Alpharetta, Georgia", "ibm appscan"): 1,
        ("Atlanta, Georgia", "ibm appscan"): 1,
        ("Dallas, Texas", "hcl appscan"): 1,
        ("Bedminster, New Jersey", "hcl appscan"): 1,
        ("Middletown, New Jersey", "hcl appscan"): 1,
        ("Bothell, Washington", "hcl appscan"): 1,
        ("Alpharetta, Georgia", "hcl appscan"): 1,
        ("Atlanta, Georgia", "hcl appscan"): 1,
        ("Dallas, Texas", "netsparker"): 1,
        ("Bedminster, New Jersey", "netsparker"): 1,
        ("Middletown, New Jersey", "netsparker"): 1,
        ("Bothell, Washington", "netsparker"): 1,
        ("Alpharetta, Georgia", "netsparker"): 1,
        ("Atlanta, Georgia", "netsparker"): 1,
        ("Dallas, Texas", "acunetix"): 1,
        ("Bedminster, New Jersey", "acunetix"): 1,
        ("Middletown, New Jersey", "acunetix"): 1,
        ("Bothell, Washington", "acunetix"): 1,
        ("Alpharetta, Georgia", "acunetix"): 1,
        ("Atlanta, Georgia", "acunetix"): 1,
        ("Dallas, Texas", "java"): 1,
        ("Bedminster, New Jersey", "java"): 1,
        ("Middletown, New Jersey", "java"): 1,
        ("Bothell, Washington", "java"): 1,
        ("Alpharetta, Georgia", "java"): 1,
        ("Atlanta, Georgia", "java"): 1,
        ("Dallas, Texas", "python"): 1,
        ("Bedminster, New Jersey", "python"): 2,
        ("Bothell, Washington", "python"): 1,
        ("Alpharetta, Georgia", "python"): 2,
        ("Atlanta, Georgia", "python"): 2,
        ("Dallas, Texas", "bash"): 1,
        ("Bedminster, New Jersey", "bash"): 1,
        ("Middletown, New Jersey", "bash"): 1,
        ("Bothell, Washington", "bash"): 1,
        ("Alpharetta, Georgia", "bash"): 1,
        ("Atlanta, Georgia", "bash"): 1,
        ("Dallas, Texas", "php"): 1,
        ("Bedminster, New Jersey", "php"): 1,
        ("Middletown, New Jersey", "php"): 1,
        ("Bothell, Washington", "php"): 1,
        ("Alpharetta, Georgia", "php"): 1,
        ("Atlanta, Georgia", "php"): 1,
        ("Dallas, Texas", "javascript"): 1,
        ("Bedminster, New Jersey", "javascript"): 1,
        ("Middletown, New Jersey", "javascript"): 1,
        ("Bothell, Washington", "javascript"): 1,
        ("Alpharetta, Georgia", "javascript"): 1,
        ("Atlanta, Georgia", "javascript"): 1,
        ("Middletown, New Jersey", "SAFe"): 1,
        ("Plano, Texas", "SAFe"): 1,
        ("Alpharetta, Georgia", "SAFe"): 1,
        ("Atlanta, Georgia", "SAFe"): 1,
        ("Bedminster, New Jersey", "SAFe"): 1,
        ("Middletown, New Jersey", "power bi"): 1,
        ("Plano, Texas", "power bi"): 1,
        ("Alpharetta, Georgia", "power bi"): 1,
        ("Bedminster, New Jersey", "power bi"): 1,
        ("Middletown, New Jersey", "python"): 2,
        ("Plano, Texas", "python"): 1,
        ("Middletown, New Jersey", "sql"): 1,
        ("Plano, Texas", "sql"): 1,
        ("Alpharetta, Georgia", "sql"): 1,
        ("Atlanta, Georgia", "sql"): 1,
        ("Bedminster, New Jersey", "sql"): 1,
        ("Middletown, New Jersey", "jira align"): 1,
        ("Plano, Texas", "jira align"): 1,
        ("Alpharetta, Georgia", "jira align"): 1,
        ("Atlanta, Georgia", "jira align"): 1,
        ("Bedminster, New Jersey", "jira align"): 1,
        ("Middletown, New Jersey", "jira cloud"): 1,
        ("Plano, Texas", "jira cloud"): 1,
        ("Alpharetta, Georgia", "jira cloud"): 1,
        ("Atlanta, Georgia", "jira cloud"): 1,
        ("Bedminster, New Jersey", "jira cloud"): 1,
        ("Middletown, New Jersey", "git"): 1,
        ("Plano, Texas", "git"): 2,
        ("Alpharetta, Georgia", "git"): 1,
        ("Atlanta, Georgia", "git"): 1,
        ("Bedminster, New Jersey", "git"): 1,
        ("Middletown, New Jersey", "servicenow"): 1,
        ("Plano, Texas", "servicenow"): 1,
        ("Alpharetta, Georgia", "servicenow"): 1,
        ("Atlanta, Georgia", "servicenow"): 1,
        ("Bedminster, New Jersey", "servicenow"): 1,
        ("Plano, Texas", "react.js"): 1,
        ("Plano, Texas", "java"): 1,
        ("Plano, Texas", "graph ql"): 1,
        ("Plano, Texas", "node.js"): 1,
        ("Plano, Texas", "mulesoft"): 1,
        ("Plano, Texas", "co-pilot"): 1,
        ("Plano, Texas", "dynatrace"): 1,
        ("Plano, Texas", "quantum metrics"): 1,
        ("Plano, Texas", "splunk"): 1,
        ("Plano, Texas", "nosql"): 1,
        ("Plano, Texas", "next.js"): 1,
        ("Plano, Texas", "typescript"): 1,
        ("Plano, Texas", "html5"): 1,
        ("Plano, Texas", "xml"): 1,
        ("Plano, Texas", "css3"): 1,
        ("Plano, Texas", "javascript"): 1,
        ("Plano, Texas", "grafana"): 1,
        ("Plano, Texas", "prometheus"): 1,
        ("Plano, Texas", "jira"): 2,
        ("Plano, Texas", "jenkins"): 1,
        ("Plano, Texas", "docker"): 1,
        ("Plano, Texas", "kubernetes"): 1,
        ("Plano, Texas", "aws"): 1,
        ("Plano, Texas", "azure"): 1,
        ("Plano, Texas", "bootstrap.js"): 1,
        ("Plano, Texas", "cassandra"): 1,
        ("Plano, Texas", "redis"): 1,
        ("Plano, Texas", "spring boot"): 1,
        ("Plano, Texas", "kafka"): 1,
        ("Alpharetta, Georgia", "excel"): 1,
        ("Alpharetta, Georgia", "jira"): 1,
        ("Alpharetta, Georgia", "powerpoint"): 1,
        ("Atlanta, Georgia", "excel"): 1,
        ("Atlanta, Georgia", "jira"): 1,
        ("Atlanta, Georgia", "power bi"): 1,
        ("Atlanta, Georgia", "powerpoint"): 1,
        ("Middletown, New Jersey", "excel"): 1,
        ("Middletown, New Jersey", "jira"): 1,
        ("Middletown, New Jersey", "powerpoint"): 1,
        ("Plano, Texas", "excel"): 1,
        ("Plano, Texas", "powerpoint"): 1,
        ("Bedminster, New Jersey", "excel"): 1,
        ("Bedminster, New Jersey", "jira"): 1,
        ("Bedminster, New Jersey", "powerpoint"): 1,
        ("Plano, Texas", "mongodb"): 1,
    }
    stack_count_assert = {
        (
            "Dallas, Texas",
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
            "Bedminster, New Jersey",
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
            "Middletown, New Jersey",
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
            "Bothell, Washington",
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
            "Alpharetta, Georgia",
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
            "Atlanta, Georgia",
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
            "Middletown, New Jersey",
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
                        "jira align",
                        "jira cloud",
                        "git",
                        "jira",
                    ]
                )
            ),
        ): 1,
        (
            "Plano, Texas",
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
                        "jira align",
                        "jira cloud",
                        "git",
                        "jira",
                    ]
                )
            ),
        ): 1,
        (
            "Alpharetta, Georgia",
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
                        "jira align",
                        "jira cloud",
                        "git",
                        "jira",
                    ]
                )
            ),
        ): 1,
        (
            "Atlanta, Georgia",
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
                        "jira align",
                        "jira cloud",
                        "git",
                        "jira",
                    ]
                )
            ),
        ): 1,
        (
            "Bedminster, New Jersey",
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
                        "jira align",
                        "jira cloud",
                        "git",
                        "jira",
                    ]
                )
            ),
        ): 1,
        (
            "Plano, Texas",
            tuple(
                sorted(
                    [
                        "aws",
                        "bootstrap.js",
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
                        "nosql",
                        "next.js",
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
async def test_requesting_workday_payload():
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
        "https://permianres.wd12.myworkdayjobs.com/wday/cxs/permianres/Permian_Resources_Careers/jobs",
        "https://cox.wd1.myworkdayjobs.com/wday/cxs/cox/Cox_External_Career_Site_1/jobs",
        "https://rockwellautomation.wd1.myworkdayjobs.com/wday/cxs/rockwellautomation/External_Rockwell_Automation/jobs",
        "https://dowjones.wd1.myworkdayjobs.com/wday/cxs/dowjones/Dow_Jones_Career/jobs",
        "https://huntingtonhospital.wd5.myworkdayjobs.com/wday/cxs/huntingtonhospital/HuntingtonHospitalCareers/jobs",
        "https://fmc.wd12.myworkdayjobs.com/wday/cxs/fmc/FMC/jobs",
        "https://hancockwhitney.wd5.myworkdayjobs.com/wday/cxs/hancockwhitney/Careers/jobs",
        "https://activision.wd1.myworkdayjobs.com/wday/cxs/activision/King_External_Careers/jobs",
        "https://fmr.wd1.myworkdayjobs.com/wday/cxs/fmr/fidelitycareers/jobs",
        "https://petco.wd1.myworkdayjobs.com/wday/cxs/petco/External/jobs",
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
        "https://stanfordhealthcare.wd5.myworkdayjobs.com/wday/cxs/stanfordhealthcare/SHC_External_Career_Site/jobs",
        "https://ngc.wd1.myworkdayjobs.com/wday/cxs/ngc/Northrop_Grumman_External_Site/jobs",
        "https://walmart.wd5.myworkdayjobs.com/wday/cxs/walmart/WalmartExternal/jobs",
        "https://thehartford.wd5.myworkdayjobs.com/wday/cxs/thehartford/Careers_Restricted/jobs",
        "https://comcast.wd5.myworkdayjobs.com/wday/cxs/comcast/Comcast_Careers/jobs",
        "https://shakeshack.wd5.myworkdayjobs.com/wday/cxs/shakeshack/External/jobs",
        "https://papajohns.wd1.myworkdayjobs.com/wday/cxs/papajohns/PapaJohnsCareers/jobs",
        "https://hcmportal.wd5.myworkdayjobs.com/wday/cxs/hcmportal/Search/jobs",
    ]
    offset = 0
    request_count = 20
    tasks = []
    tor_sem = asyncio.Semaphore(3)
    for uri in urls:
        task = asyncio.create_task(
            _request_job_posts(uri, offset, request_count, tor_sem), name=uri
        )
        tasks.append(task)

    for task in tasks:
        job_posts = await task
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
    tor_sem = asyncio.Semaphore(3)

    job_count_task = asyncio.create_task(_request_job_count(url, tor_sem))
    job_count = await job_count_task

    for offset in range(0, job_count, 20):
        task = asyncio.create_task(_request_job_posts(url, offset, 20, tor_sem))
        job_post_tasks.append(task)

    for task in job_post_tasks:
        res = await task
        count += len(res)

    return count


# create urls list with multiple workday urls
# create list of tasks to retrieve each urls number of jobs
# create list of tasks to count number of workday job post
# assert that the number of jobs to number of retrieved posts is equal
@pytest.mark.asyncio
async def test_number_of_jobs_retrieved():
    """Test if number of jobs retrieved is equal to number of jobs advertised."""
    url = "https://walmart.wd5.myworkdayjobs.com/wday/cxs/walmart/WalmartExternal/jobs"
    tor_sem = asyncio.Semaphore(3)
    num_listed_task = asyncio.create_task(_request_job_count(url, tor_sem))
    count_task = asyncio.create_task(count_job_posts(url))

    listed_num = await num_listed_task
    counted_num = await count_task

    assert listed_num == counted_num


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
    sensitive = re.compile(r"(?: |>|\.|\(|(?<=/))SAFe(?: |>|\.|,|(?=/)|\))")
    insensitive = re.compile(
        r"(?: |>|\.|\(|(?<=/))dast(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))burp suite(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))ibm appscan(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))hcl appscan(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))netsparker(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))acunetix(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))java(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))python(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))bash(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))php(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))javascript(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))power bi(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))sql(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))excel(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))powerpoint(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))jira align(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))jira cloud(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))git(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))servicenow(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))react js(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))graph ql(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))node js(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))mulesoft(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))co-pilot(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))dynatrace(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))quantum metrics(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))splunk(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))next.js(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))node.js(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))react.js(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))copilots(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))no sql(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))next js(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))typescript(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))bootstrap.js(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))html5(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))xml(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))css3(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))nosql(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))cassandra(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))mongodb(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))mongo db(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))spring boot(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))kafka(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))redis(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))azure(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))aws(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))prometheus(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))jira(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))jenkins(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))docker(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))grafana(?: |>|\.|,|(?=/)|\))|(?: |>|\.|\(|(?<=/))kubernetes(?: |>|\.|,|(?=/)|\))"
    )
    synonyms = {
        "node js": "node.js",
        "react js": "react.js",
        "copilots": "co-pilot",
        "next js": "next.js",
        "no sql": "nosql",
        "mongo db": "mongodb",
    }
    parents = {"jira align": "jira", "jira cloud": "jira"}

    res = await parse_workday(
        date, urls, location_list, sensitive, insensitive, synonyms, parents
    )
    assert res[0] != {} and res[1] != {}
