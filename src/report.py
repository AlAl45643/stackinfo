import datetime as dt
import json
import os
from datetime import date
from dateutil.relativedelta import relativedelta

import requests
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from sql import Locations


def _get_locations():
    user = os.getenv("DATABASE_USERNAME")
    passw = os.getenv("DATABASE_PASSWORD")
    name = os.getenv("DATABASE_NAME")
    container = os.getenv("DATABASE_CONTAINER_NAME")
    engine = create_engine(
        f"postgresql+psycopg2://{user}:{passw}@{container}:5432/{name}"
    )
    query = select(Locations.city, Locations.state)

    with Session(engine) as session:
        locations = session.execute(query).all()

    return locations


def _get_tech_report(date: dt.date, locations: list[tuple[str, str]]) -> str:
    report = f"""
# {date.year}-0{date.month}"""

    container = os.getenv("FASTAPI_CONTAINER_NAME")
    url = f"http://{container}:80/reports/tech"
    for location in locations:
        city, state = location[0], location[1]
        report += f"""
## {city}, {state}"""
        report += """
<table>
 <thead>
  <tr>
   <th>Name</th>
   <th>Count</th>
  </tr>
 </thead>
 <tbody>
"""
        result = requests.get(f"{url}?date={date}&city={city}&state={state}")
        result = json.loads(result.text)
        for tech in result:
            name = tech[0]
            count = tech[1]
            report += f"""
  <tr>
   <td>{name}</td>
   <td>{count}</td>
  </tr>"""

        report += """
 </tbody>
</table>
"""
    return report


def _get_stack_report(date: dt.date, locations: list[str]) -> str:
    report = f"""
# {date.year}-0{date.month}"""

    container = os.getenv("FASTAPI_CONTAINER_NAME")
    url = f"http://{container}:80/reports/stack"
    for location in locations:
        city, state = location[0], location[1]
        report += f"""
## {city}, {state}"""
        report += """
<table>
 <thead>
  <tr>
   <th>Name</th>
   <th>Count</th>
  </tr>
 </thead>
 <tbody>
"""
        result = requests.get(f"{url}?date={date}&city={city}&state={state}")
        result = json.loads(result.text)
        for tech in result:
            name = tech[0]
            count = tech[1]
            report += f"""
  <tr>
   <td>{name}</td>
   <td>{count}</td>
  </tr>"""

        report += """
 </tbody>
</table>
"""
    return report


def main(today: dt.date):
    locations = _get_locations()
    tech_report = _get_tech_report(today, locations)
    stack_report = _get_stack_report(today, locations)

    tech_report_file = open(f"reports/tech_report_{today.year}_{today.month}", "x")
    tech_report_file.write(tech_report)

    stack_report_file = open(f"reports/stack_report_{today.year}_{today.month}", "x")
    stack_report_file.write(stack_report)


if __name__ == "__main__":
    today = date.today()
    if today.day == 1:
        yesterday = today - relativedelta(days=1)
        main(yesterday)
