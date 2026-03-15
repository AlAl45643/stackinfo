import asyncio
import datetime as dt
import os
import re
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from scrape_workday import Scrape
from sql import Locations, Tech, Tech_Parent_Tech, Tech_Synonym, WorkdayURLs

# from scrape_workday import parse_workday


# get date
# get location_list
# get sensitive
# get insensitive
# get synonyms
# get parents
# get workday uris
# call parse_workday
# create database
# store in database
async def scrape(date: dt.date | None):
    load_dotenv()
    user = os.getenv("DATABASE_USERNAME")
    passw = os.getenv("DATABASE_PASSWORD")
    name = os.getenv("DATABASE_NAME")
    engine = create_engine(
        f"postgresql+psycopg2://{user}:{passw}@localhost:5432/{name}"
    )

    workday_urls_query = select(WorkdayURLs.url)
    location_query = select(Locations.city, Locations.state)
    sensitive_query = select(Tech.name).where(Tech.case_sensitive == True)
    insensitive_query = select(Tech.name).where(Tech.case_sensitive == False)
    synonym_query = select(Tech_Synonym.synonym, Tech_Synonym.name)
    parents_query = select(Tech_Parent_Tech.child_name, Tech_Parent_Tech.parent_name)
    with Session(engine) as session:
        workday_urls = session.scalars(workday_urls_query).all()
        locations = session.execute(location_query).all()
        sensitive_list = session.scalars(sensitive_query).all()
        insensitive_list = session.scalars(insensitive_query).all()
        synonyms = session.execute(synonym_query).all()
        parents = session.execute(parents_query).all()

    sensitive = ""
    for s in sensitive_list:
        sensitive += r"(?: |>|\.|\(|(?<=/))" + s + r"(?: |>|\.|,|(?=/)|\))"
        if s != sensitive_list[-1]:
            sensitive += "|"
    sensitive = re.compile(sensitive)

    insensitive = ""
    for s in insensitive_list:
        insensitive += r"(?: |>|\.|\(|(?<=/))" + s + r"(?: |>|\.|,|(?=/)|\))"
        if s != insensitive_list[-1]:
            insensitive += "|"
    insensitive = re.compile(insensitive)
    synonyms = dict(synonyms)
    parents = dict(parents)

    scrape = Scrape(asyncio.Semaphore(3))
    task = asyncio.create_task(
        scrape.parse_workday(
            date, workday_urls, locations, sensitive, insensitive, synonyms, parents
        )
    )
    res = await task

    return res


def main(date: dt.date | None) -> None:
    return asyncio.run(scrape(date))


if __name__ == "__main__":
    if len(sys.argv) == 3:
        print(main(dt.date.strptime(sys.argv[1], "%Y-%m-%d")))
    else:
        print(main(None))
