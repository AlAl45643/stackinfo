import json
import datetime as dt
import os
from fastapi import FastAPI
from sqlalchemy import text, create_engine
from dateutil.relativedelta import relativedelta


app = FastAPI()


# compare = set(first)
# count = 0
# for tech in second
#  if tech in compare
#   count += 1
# return count / len(second)


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


# change = True
# while change:
#  old_stack = stack
#  while i < len(stacks)
#   j = i + 1
#   while j < len(stacks)
#    if diff(stack[i][0], stack[j][0]) < percent:
#      stack[i][1], stack[i][2] += stack[j][1], stack[j][2]
#      stack.removeat(j)
#
#   i+=1
# if old_stack == stack
#  change = False
# return stacks
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
                    stacks[i][2] += stacks[j][2]
                    stacks[i][0] = _stack_combine(stacks[i][0], stacks[j][0])
                    del stacks[j]
                j += 1
            i += 1
        if old_stacks == stacks:
            change = False
    return stacks


# 66% similar stack combine
# Input: [[['python', 'sql'], 3], [['python', 'sql', 'pandas'], 2], [['java', 'react'], 1]]
# Output:[[['python', 'sql'], 5], [['java', 'react'], 1]]
# @app.get("/reports/stack", response_class=HTMLResponse)
# query database for stack and count
# join together counts and stacks based on similarity
#
# return json
@app.get("/reports/stack")
async def view_stack_report(
    date: dt.date = dt.date(2026, 5, 3),
    city: str = "atlanta",
    state: str = "georgia",
    percent: int = 50,
):
    user = os.getenv("DATABASE_USERNAME")
    passw = os.getenv("DATABASE_PASSWORD")
    name = os.getenv("DATABASE_NAME")
    container = os.getenv("DATABASE_CONTAINER_NAME")
    engine = create_engine(
        f"postgresql+psycopg2://{user}:{passw}@{container}:5432/{name}"
    )

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

),
  prev_rank AS (
    SELECT agg.stack, SUM(stack.count) count
      FROM stack_count stack
           INNER JOIN aggregate_stacks agg
               ON stack.id = agg.stack_count_id
     WHERE extract(year FROM stack.date)::int = :p_year AND extract(month FROM stack.date) = :p_month AND stack.city = :city AND stack.state = :state
     GROUP BY agg.stack
     ORDER BY SUM(stack.count) DESC

  )

SELECT agg.stack, SUM(stack.count) count,
       CASE
       WHEN (SELECT p.count FROM prev_rank p WHERE agg.stack = p.stack) IS NULL THEN 0
       ELSE (SELECT p.count FROM prev_rank p WHERE agg.stack = p.stack)
       END prev_count
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
                "city": city,
                "state": state,
                "year": year,
                "month": month,
            },
        )
    result = [list(i) for i in result]
    result = _combine_stacks(result, percent)
    result = [[i[0], i[1], 0 if i[2] == 0 else i[1] - i[2]] for i in result]
    result.sort(key=lambda i: i[1], reverse=True)
    return json.dumps(result)


# query database
# return as json
@app.get("/reports/tech")
async def view_tech_report(
    date: dt.date = dt.date(2026, 5, 3), city: str = "atlanta", state: str = "georgia"
):
    user = os.getenv("DATABASE_USERNAME")
    passw = os.getenv("DATABASE_PASSWORD")
    name = os.getenv("DATABASE_NAME")
    container = os.getenv("DATABASE_CONTAINER_NAME")
    engine = create_engine(
        f"postgresql+psycopg2://{user}:{passw}@{container}:5432/{name}"
    )

    year = date.year
    month = date.month
    p_date = date - relativedelta(months=1)
    p_year = p_date.year
    p_month = p_date.month
    with engine.connect() as conn:
        result = conn.execute(
            text("""WITH prev_rank AS (
  SELECT tech.name, dense_rank() over (ORDER BY SUM(tech.count) DESC) rank
    FROM tech_count tech
   WHERE extract(year FROM tech.date)::int = :p_year AND extract(month FROM tech.date)::int = :p_month AND tech.city = :city AND tech.state = :state
   GROUP BY tech.name
   ORDER BY SUM(tech.count) desc
)                                                                                                         
SELECT tech.name, SUM(tech.count) count, dense_rank() over (ORDER BY SUM(tech.count) DESC) rank,
       CASE
       WHEN (
         SELECT prev.rank                                           
           FROM prev_rank prev
          WHERE tech.name = prev.name
       ) IS NULL THEN 0
       ELSE (
         SELECT prev.rank                                           
           FROM prev_rank prev
          WHERE tech.name = prev.name
       ) - dense_rank() over (ORDER BY SUM(tech.count) DESC)
       END monthly_rank_change 
  FROM tech_count tech
 WHERE extract(year FROM tech.date)::int = :year AND extract(month FROM tech.date)::int = :month AND tech.city = :city AND tech.state = :state
 GROUP BY tech.name                                                                                                                    
 ORDER BY SUM(tech.count) DESC
"""),
            {
                "p_year": p_year,
                "p_month": p_month,
                "city": city,
                "city": city,
                "state": state,
                "year": year,
                "month": month,
            },
        )
    result = [list(i) for i in result]
    result.sort(key=lambda i: i[1], reverse=True)
    return json.dumps(result)
