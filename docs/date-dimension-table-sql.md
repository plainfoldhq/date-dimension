# Date dimension table (dim_date) in SQL: build and load

A date dimension table is a table with one row per calendar day. Each row holds the date and many derived columns: month name, quarter, weekday, weekend flag, fiscal period and so on. You join your fact tables to it instead of repeating date logic in every query. It is also called `dim_date` or a calendar table. This guide shows how to build one with `retailcal`, a fiscal calendar Python library, and load it into SQLite, PostgreSQL or any tool that reads CSV.

## Guides

- [Retail 4-4-5 / 4-5-4 / 5-4-4 calendar explained](retail-445-454-544-calendar-explained.md)
- [Date dimension table in SQL](date-dimension-table-sql.md) (this page)
- Back to the [retailcal README](../README.md)

## What a dim_date table is for

- Group sales by month, quarter, fiscal period or fiscal week with a simple join.
- Filter weekends, or any day type you define, without date functions in each query.
- Keep fiscal and retail calendar logic in one place.
- Fill gaps: a day with no sales still has a row in `dim_date`.

## Typical columns

| Column | Example | Notes |
|---|---|---|
| `date_key` | `20251128` | Integer `YYYYMMDD`. Common primary key. |
| `date` | `2025-11-28` | The calendar date. |
| `year`, `quarter`, `month` | `2025`, `4`, `11` | Calendar parts. |
| `month_name`, `day_name` | `November`, `Friday` | For reports. |
| `day_of_month` | `28` | |
| `day_of_week_iso` | `5` | 1 = Monday, 7 = Sunday. |
| `is_weekend` | `0` or `1` | |
| `fiscal_year` | `2025` | From the fiscal calendar. |
| `fiscal_quarter`, `fiscal_period`, `fiscal_week` | `4`, `10`, `43` | |
| `week_start`, `week_end` | `2025-11-23`, `2025-11-29` | Fiscal week dates. |
| `is_53_week_year` | `0` or `1` | |

Other columns people add: ISO week, holiday flags, business-day flags, and days in month.

## Generate the table with retailcal

`retailcal` produces the fiscal columns. You add the calendar columns with the standard library. This script writes 2024 to 2026 using the NRF-style 4-5-4 preset. It was run with `PYTHONPATH=src python3` on Python 3.11.

```python
# build_dim.py
import csv
from datetime import date, timedelta
import retailcal

cal = retailcal.Calendar(*retailcal.PRESETS["nrf-454"])
start, end = date(2024, 1, 1), date(2026, 12, 31)

cols = ["date_key", "date", "year", "quarter", "month", "month_name",
        "day_of_month", "day_of_week_iso", "day_name", "is_weekend"]
fiscal = ["fiscal_year", "fiscal_quarter", "fiscal_period", "fiscal_week",
          "week_start", "week_end", "is_53_week_year"]

with open("dim_date.csv", "w", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(cols + fiscal)
    d = start
    while d <= end:
        r = cal.row(d)
        w.writerow([d.strftime("%Y%m%d"), d.isoformat(), d.year, (d.month - 1) // 3 + 1,
                    d.month, d.strftime("%B"), d.day, d.isoweekday(), d.strftime("%A"),
                    int(d.isoweekday() >= 6)] + [r[c] for c in fiscal])
        d += timedelta(days=1)
```

Run it:

```
PYTHONPATH=src python3 build_dim.py
```

The file has a header and 1,096 data rows. The first data row:

```
20240101,2024-01-01,2024,1,1,January,1,1,Monday,0,2023,4,12,49,2023-12-31,2024-01-06,1
```

January 1 2024 belongs to NRF fiscal 2023, which has 53 weeks, so `is_53_week_year` is 1.

For other calendars, change the preset. For example, use `"445-sat-nearest-dec"` for a 4-4-5 calendar. See the [calendar guide](retail-445-454-544-calendar-explained.md).

## Load into SQLite

The `sqlite3` module ships with Python. This script creates the table, loads the CSV and runs a check. I ran it as shown.

```python
# load_sqlite.py
import csv, sqlite3

con = sqlite3.connect("dim_date.db")
con.execute("DROP TABLE IF EXISTS dim_date")
con.execute("""CREATE TABLE dim_date (
  date_key INTEGER PRIMARY KEY, date TEXT NOT NULL, year INTEGER, quarter INTEGER,
  month INTEGER, month_name TEXT, day_of_month INTEGER, day_of_week_iso INTEGER,
  day_name TEXT, is_weekend INTEGER, fiscal_year INTEGER, fiscal_quarter INTEGER,
  fiscal_period INTEGER, fiscal_week INTEGER, week_start TEXT, week_end TEXT,
  is_53_week_year INTEGER)""")
with open("dim_date.csv", newline="") as f:
    rows = list(csv.reader(f))[1:]
con.executemany("INSERT INTO dim_date VALUES (%s)" % ",".join("?" * 17), rows)
con.commit()
for r in con.execute("""SELECT fiscal_year, fiscal_period, COUNT(*) AS days
    FROM dim_date WHERE fiscal_year = 2025 GROUP BY 1, 2 ORDER BY 2 LIMIT 4"""):
    print(r)
print(con.execute("SELECT COUNT(*), MIN(date), MAX(date) FROM dim_date").fetchone())
```

Output:

```
(2025, 1, 28)
(2025, 2, 35)
(2025, 3, 28)
(2025, 4, 28)
(1096, '2024-01-01', '2026-12-31')
```

Periods 1 to 4 of a 4-5-4 year have 28, 35, 28 and 28 days: 4, 5, 4 and 4 weeks.

Dates are stored as ISO text (`YYYY-MM-DD`), which sorts and compares correctly in SQLite.

## Load into PostgreSQL

Create the table, then use `\copy` in `psql`. `\copy` reads the file from your machine, not the server. I did not run these Postgres commands against a server for this guide, so test them on your own database first.

```sql
CREATE TABLE dim_date (
  date_key        integer PRIMARY KEY,
  date            date NOT NULL,
  year            smallint,
  quarter         smallint,
  month           smallint,
  month_name      text,
  day_of_month    smallint,
  day_of_week_iso smallint,
  day_name        text,
  is_weekend      smallint,
  fiscal_year     smallint,
  fiscal_quarter  smallint,
  fiscal_period   smallint,
  fiscal_week     smallint,
  week_start      date,
  week_end        date,
  is_53_week_year smallint
);

\copy dim_date FROM 'dim_date.csv' WITH (FORMAT csv, HEADER true)
```

The columns in the CSV are in the same order as the table, so no column list is needed. Check the load:

```sql
SELECT count(*), min(date), max(date) FROM dim_date;
```

## Load from a generic CSV import

Any tool that imports CSV can read this file. I did not test other tools, so check these settings in yours:

- The file is UTF-8, uses commas, and has a header row.
- Lines end with `\n`.
- Dates are ISO `YYYY-MM-DD`. Tell the importer to read `date`, `week_start` and `week_end` as dates, not text.
- `date_key` is an integer, not a date.

## Use it in a query

Join your fact table on the date. This example is a pattern, not run here: it assumes an `orders` table with an `order_date` column.

```sql
SELECT d.fiscal_year, d.fiscal_period, sum(o.amount) AS sales
FROM orders o
JOIN dim_date d ON d.date = o.order_date
GROUP BY d.fiscal_year, d.fiscal_period
ORDER BY d.fiscal_year, d.fiscal_period;
```

## Want it ready-made?

The [date dimension + retail calendar pack](https://buy.polar.sh/polar_cl_dQIvyRLcbGYoTfZgVmsIENITeo4Zu2zok8JI94KfqWn?utm_source=github&utm_medium=readme&utm_campaign=C&utm_content=date-dimension) ($19, one-time; Polar is the merchant of record and handles sales tax) has it built:

- `dim_date` for 2000-2050 (18,628 rows, 45 columns, including US holidays and NYSE trading days) as CSV and SQLite
- Four precomputed fiscal calendars 2000-2050 (NRF 4-5-4 and three 4-4-5 / 5-4-4 variants) and a fiscal-year summary table
- PostgreSQL tables + a tested load script, and a dbt seed config with column types and tests

It is also in the [calendar data bundle](https://buy.polar.sh/polar_cl_HiUeTqJE1gUqHdb3OlOWb6Jml7pdq8E71O2pA4Y9iQ3?utm_source=github&utm_medium=readme&utm_campaign=BUNDLE&utm_content=date-dimension) (US business-day calendar, date dimension and time zone packs) for $35 instead of $49. Full contents: [README](../README.md).

---

Made by Plainfold. Written with AI assistance.
