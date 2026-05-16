import datetime as dt
import os
from fastapi import FastAPI
from sqlalchemy import text, create_engine
from dateutil.relativedelta import relativedelta


app = FastAPI()


def _create_engine():
    user = os.getenv("DATABASE_USERNAME")
    passw = os.getenv("DATABASE_PASSWORD")
    name = os.getenv("DATABASE_NAME")
    container = os.getenv("DATABASE_CONTAINER_NAME")
    engine = create_engine(
        f"postgresql+psycopg2://{user}:{passw}@{container}:5432/{name}"
    )
    return engine


def _stack_combine(first: list[str], second: list[str]):
    res = []
    s2 = set(second)
    for tech in first:
        if tech in s2:
            res.append(tech)

    return res


def _stack_compare(first: list[str], second: list[str]):
    main = max(first, second, key=lambda i: len(i))
    if main == first:
        compare = second
    else:
        compare = first

    s = set(compare)
    count = 0
    for tech in main:
        if tech in s:
            count += 1
    return (count / len(main)) * 100


def _combine_stacks(stacks: list[list], percent: int):
    change = True
    while change:
        old_stacks = stacks.copy()
        i = 0
        while i < len(stacks):
            j = i + 1
            while j < len(stacks):
                if _stack_compare(stacks[i][0], stacks[j][0]) >= percent:
                    stacks[i][1] += stacks[j][1]
                    stacks[i][0] = _stack_combine(stacks[i][0], stacks[j][0])
                    del stacks[j]
                j += 1
            i += 1
        if old_stacks == stacks:
            change = False
    return stacks


@app.get("/reports/stack")
async def view_stack_report(
    date: dt.date = dt.date(2026, 5, 3),
    city: str = "atlanta",
    state: str = "georgia",
    percent: int = 50,
):
    engine = _create_engine()
    year = date.year
    month = date.month
    p_date = date - relativedelta(months=1)
    p_year = p_date.year
    p_month = p_date.month
    with engine.connect() as conn:
        result = conn.execute(
            text("""WITH aggregate_stacks AS (
  SELECT t.stack_count_id, jsonb_agg(name ORDER BY name) stack
    FROM tech_stack_count t
   GROUP BY t.stack_count_id

)

SELECT agg.stack, SUM(stack.count) count
  FROM stack_count stack
       INNER JOIN aggregate_stacks agg
           ON stack.id = agg.stack_count_id
 WHERE extract(year FROM stack.date)::int = :year AND extract(month FROM stack.date) = :month AND stack.city = :city AND stack.state = :state
 GROUP BY agg.stack
 ORDER BY SUM(stack.count) DESC
"""),
            {
                "p_year": p_year,
                "p_month": p_month,
                "city": city,
                "state": state,
                "year": year,
                "month": month,
            },
        )
    result = [list(i) for i in result]
    result = _combine_stacks(result, percent)
    result.sort(key=lambda i: i[1], reverse=True)
    return result


# query database
# return as json
@app.get("/reports/tech")
async def view_tech_report(
    date: dt.date = dt.date(2026, 5, 3), city: str = "atlanta", state: str = "georgia"
):
    engine = _create_engine()
    year = date.year
    month = date.month
    p_date = date - relativedelta(months=1)
    p_year = p_date.year
    p_month = p_date.month
    with engine.connect() as conn:
        result = conn.execute(
            text("""                                                                                     
SELECT tech.name, SUM(tech.count) count 
  FROM tech_count tech
 WHERE extract(year FROM tech.date)::int = :year AND extract(month FROM tech.date)::int = :month AND tech.city = :city AND tech.state = :state
 GROUP BY tech.name                                                                                                                    
 ORDER BY SUM(tech.count) DESC
"""),
            {
                "p_year": p_year,
                "p_month": p_month,
                "city": city,
                "state": state,
                "year": year,
                "month": month,
            },
        )
    result = [list(i) for i in result]
    result.sort(key=lambda i: i[1], reverse=True)
    return result
