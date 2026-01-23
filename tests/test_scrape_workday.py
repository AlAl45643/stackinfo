import json
from src.scrape_workday import _retrieve_locations, _retrieve_tech
import re
import os


# create techs and stacks dicts
# parse locations from workday response
# parse techs from workday response
# assign appropiate values to techs and stacks
# assert techs and stacks are equal to correct parse


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
