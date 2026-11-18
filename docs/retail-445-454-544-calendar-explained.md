# The 4-4-5, 4-5-4 and 5-4-4 retail calendar, explained

A 4-4-5 calendar is a retail calendar. It splits a fiscal year into 12 periods built from whole weeks. Retailers use it so every period has the same weekdays and results compare cleanly year over year. This guide explains the three patterns, how 52/53-week years work, and how to build them with `retailcal`, a fiscal calendar Python library with no dependencies.

## Guides

- [Retail 4-4-5 / 4-5-4 / 5-4-4 calendar explained](retail-445-454-544-calendar-explained.md) (this page)
- [Date dimension table in SQL](date-dimension-table-sql.md)
- Back to the [retailcal README](../README.md)

## What 4-4-5, 4-5-4 and 5-4-4 mean

A fiscal year has 4 quarters. Each quarter has 13 weeks. The three numbers say how many weeks go in each of the quarter's three periods.

| Pattern | Weeks per period in a quarter | Weeks per quarter |
|---|---|---|
| 4-4-5 | 4, 4, 5 | 13 |
| 4-5-4 | 4, 5, 4 | 13 |
| 5-4-4 | 5, 4, 4 | 13 |

The same pattern repeats in all four quarters. A 52-week year has 12 periods. For example, 4-5-4 gives `4-5-4-4-5-4-4-5-4-4-5-4`.

Every period starts and ends on the same weekday, so a period is always whole weeks. That is the main difference from a calendar month.

## 52-week and 53-week years

52 weeks is 364 days. A real year has 365 or 366 days. If the fiscal year always had 52 weeks, it would drift away from the calendar by one or two days a year. So some years have 53 weeks.

The 53rd week is not chosen by hand. It follows from the rule that decides when the year ends.

## The rules retailcal implements

A fiscal year always ends on one chosen weekday (for example, Saturday). The code supports two rules for picking the year-end date in the end month:

- `nearest`: the year ends on that weekday nearest the last day of the end month. If the last day of the month is itself that weekday, it is the year end. Otherwise, if the last such weekday is 0 to 3 days before the month end, use it. If it is 4 to 6 days before, use the next one, which falls in the following month.
- `last`: the year ends on the last such weekday of the end month.

A year starts the day after the previous year ends. The length of the year is then the number of whole weeks between the two dates. It is 52 or 53 weeks. A year has 53 weeks when the two year-end dates are 371 days apart rather than 364.

When a year has 53 weeks, the extra week is added to period 12 by default. In a 4-5-4 year the last period then has 5 weeks (`4-5-4-4-5-4-4-5-4-4-5-5`). In a 4-4-5 year it has 6. You can move the extra week with `extra_week_period` (or `--extra-week-period` on the command line).

Fiscal years are named one of two ways:

- `start`: named by the calendar year in which the year starts.
- `end`: named by the calendar year in which the year ends.

### The NRF-style preset

The `nrf-454` preset uses: end month January, Saturday, `nearest`, 4-5-4, `start` naming. In plain words, the year ends on the Saturday nearest January 31, and fiscal 2025 runs from February 2 2025 to January 31 2026. "NRF-style" means the rule commonly published by the National Retail Federation. This project is not affiliated with or endorsed by the NRF. Companies use their own variants, so check yours.

Built-in presets:

| Preset | Pattern | Year ends | Naming |
|---|---|---|---|
| `nrf-454` | 4-5-4 | Saturday nearest January 31 | start year |
| `445-sat-nearest-dec` | 4-4-5 | Saturday nearest December 31 | end year |
| `544-sat-nearest-dec` | 5-4-4 | Saturday nearest December 31 | end year |
| `445-sat-last-sep` | 4-4-5 | last Saturday of September | end year |

## NRF 4-5-4 fiscal years 2020 to 2030

From `sample/nrf_454_fiscal_years_2020_2030.csv`:

| Fiscal year | Start | End | Weeks |
|---|---|---|---|
| 2020 | 2020-02-02 | 2021-01-30 | 52 |
| 2021 | 2021-01-31 | 2022-01-29 | 52 |
| 2022 | 2022-01-30 | 2023-01-28 | 52 |
| 2023 | 2023-01-29 | 2024-02-03 | 53 |
| 2024 | 2024-02-04 | 2025-02-01 | 52 |
| 2025 | 2025-02-02 | 2026-01-31 | 52 |
| 2026 | 2026-02-01 | 2027-01-30 | 52 |
| 2027 | 2027-01-31 | 2028-01-29 | 52 |
| 2028 | 2028-01-30 | 2029-02-03 | 53 |
| 2029 | 2029-02-04 | 2030-02-02 | 52 |
| 2030 | 2030-02-03 | 2031-02-01 | 52 |

## Compute a retail calendar with retailcal

`retailcal` uses only the Python standard library. The examples below were run from a clone with `PYTHONPATH=src python3`, on Python 3.11.

### Find a fiscal year's dates and look up a day

```python
from datetime import date
import retailcal

cal = retailcal.Calendar(*retailcal.PRESETS["nrf-454"])
print(cal.bounds(2025))
r = cal.row(date(2025, 11, 28))
for k in ("fiscal_year", "fiscal_quarter", "fiscal_period", "fiscal_week",
          "week_of_period", "period_start", "period_end"):
    print(k, r[k])
```

Output:

```
(datetime.date(2025, 2, 2), datetime.date(2026, 1, 31))
fiscal_year 2025
fiscal_quarter 4
fiscal_period 10
fiscal_week 43
week_of_period 4
period_start 2025-11-02
period_end 2025-11-29
```

`cal.row(d)` returns a dict with 16 keys, including `day_of_fiscal_year`, `week_start`, `week_end`, `weeks_in_year` and `is_53_week_year`.

### See a 53-week year

```python
import retailcal

cal = retailcal.Calendar(*retailcal.PRESETS["nrf-454"])
for y in cal.year_rows(2022, 2024):
    print(y)
print(cal.period_lengths(2023))
```

Output:

```
{'fiscal_year': 2022, 'fiscal_year_start': '2022-01-30', 'fiscal_year_end': '2023-01-28', 'weeks': 52, 'period_weeks': '4-5-4-4-5-4-4-5-4-4-5-4'}
{'fiscal_year': 2023, 'fiscal_year_start': '2023-01-29', 'fiscal_year_end': '2024-02-03', 'weeks': 53, 'period_weeks': '4-5-4-4-5-4-4-5-4-4-5-5'}
{'fiscal_year': 2024, 'fiscal_year_start': '2024-02-04', 'fiscal_year_end': '2025-02-01', 'weeks': 52, 'period_weeks': '4-5-4-4-5-4-4-5-4-4-5-4'}
([4, 5, 4, 4, 5, 4, 4, 5, 4, 4, 5, 5], 53)
```

### Build a 4-4-5 or 5-4-4 calendar

```python
import retailcal

# 4-4-5, year ends on the last Sunday of June, named by end year
cal = retailcal.Calendar(6, "sun", rule="last", pattern="445", naming="end")
print(cal.bounds(2025))
print(cal.period_lengths(2025))

# 5-4-4 ending Saturday nearest Dec 31
c2 = retailcal.Calendar(*retailcal.PRESETS["544-sat-nearest-dec"])
print(c2.bounds(2024), c2.period_lengths(2024)[0])

# 4-4-5 with a 53rd week: the extra week lands in period 12
c3 = retailcal.Calendar(*retailcal.PRESETS["445-sat-nearest-dec"])
print(c3.bounds(2020), c3.period_lengths(2020))
```

Output:

```
(datetime.date(2024, 7, 1), datetime.date(2025, 6, 29))
([4, 4, 5, 4, 4, 5, 4, 4, 5, 4, 4, 5], 52)
(datetime.date(2023, 12, 31), datetime.date(2024, 12, 28)) [5, 4, 4, 5, 4, 4, 5, 4, 4, 5, 4, 4]
(datetime.date(2019, 12, 29), datetime.date(2021, 1, 2)) ([4, 4, 5, 4, 4, 5, 4, 4, 5, 4, 4, 6], 53)
```

### List the 53-week years

```python
import retailcal

for name in ("nrf-454", "445-sat-nearest-dec", "544-sat-nearest-dec"):
    cal = retailcal.Calendar(*retailcal.PRESETS[name])
    print(name, [y["fiscal_year"] for y in cal.year_rows(2000, 2030) if y["weeks"] == 53])
```

Output:

```
nrf-454 [2000, 2006, 2012, 2017, 2023, 2028]
445-sat-nearest-dec [2003, 2008, 2014, 2020, 2025]
544-sat-nearest-dec [2003, 2008, 2014, 2020, 2025]
```

### Use the command line

```
PYTHONPATH=src python3 -m retailcal --preset nrf-454 --year-table --from 2020 --to 2030
PYTHONPATH=src python3 -m retailcal --preset nrf-454 --from 2020 --to 2030 > nrf_454.csv
PYTHONPATH=src python3 -m retailcal --end-month 6 --weekday sun --rule last \
    --pattern 445 --naming end --from 2015 --to 2035 > my_calendar.csv
```

The first command prints one row per fiscal year. The others write one row per day. The year-table output for 2020 to 2030 has the same values as the sample CSV above (the sample adds a leading `calendar` column).

The daily CSV has 16 columns: `date`, `fiscal_year`, `fiscal_quarter`, `fiscal_period`, `fiscal_week`, `week_of_period`, `day_of_fiscal_year`, `day_of_fiscal_week`, `fiscal_year_start`, `fiscal_year_end`, `period_start`, `period_end`, `week_start`, `week_end`, `weeks_in_year`, `is_53_week_year`.

## Limits

- Your company may use a different year-end rule, a different place for the 53rd week, or its own naming. Set the options to match your finance team's documentation.
- For a full date table that joins these columns to calendar columns, see the [date dimension table guide](date-dimension-table-sql.md).
- Not accounting or tax advice.

---

Made by Plainfold. Written with AI assistance.
