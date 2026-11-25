# Date dimension and 4-4-5 / 4-5-4 retail calendar generator

[![tests](https://github.com/plainfoldhq/date-dimension/actions/workflows/tests.yml/badge.svg)](https://github.com/plainfoldhq/date-dimension/actions/workflows/tests.yml)

`retailcal` builds any 52/53-week fiscal or retail calendar (4-4-5, 4-5-4, 5-4-4) as CSV: fiscal year, quarter, period, week, week of period, day of fiscal year, and period/week start and end dates. It needs Python 3 and nothing else (standard library only).

Install with `pip install retailcal` or run from a clone with `PYTHONPATH=src python3 -m retailcal ...`.

```
# NRF-style 4-5-4 retail calendar (year ends Saturday nearest January 31)
retailcal --preset nrf-454 --from 2020 --to 2030 > nrf_454.csv

# One row per fiscal year: start, end, 52 or 53 weeks, weeks per period
retailcal --preset nrf-454 --year-table --from 2020 --to 2030

# Your own: 4-4-5, year ends on the last Sunday of June, named by end year
retailcal --end-month 6 --weekday sun --rule last --pattern 445 \
    --naming end --from 2015 --to 2035 > my_calendar.csv
```

From Python:

```python
from datetime import date
import retailcal
cal = retailcal.Calendar(*retailcal.PRESETS["nrf-454"])
cal.bounds(2025)            # (date(2025, 2, 2), date(2026, 1, 31))
cal.row(date(2025, 11, 28)) # fiscal year, quarter, period, week, ...
```

Presets: `nrf-454`, `445-sat-nearest-dec`, `544-sat-nearest-dec`, `445-sat-last-sep`. Rules: `nearest` = the year ends on the chosen weekday nearest the last day of the end month; `last` = the last such weekday of the month. A 53rd week goes to period 12 unless `--extra-week-period` says otherwise.

## Reference pages

[4-5-4 retail calendar by fiscal year](https://plainfoldhq.github.io/retail-calendar-4-5-4/) and [53-week fiscal years 2000-2050](https://plainfoldhq.github.io/53-week-fiscal-years/), generated with `retailcal`. For ISO 8601 weeks: [ISO week numbers by year](https://plainfoldhq.github.io/week-numbers/).

## Guides
- [4-4-5, 4-5-4 and 5-4-4 retail calendars explained (52/53-week years)](https://github.com/plainfoldhq/date-dimension/blob/main/docs/retail-445-454-544-calendar-explained.md)
- [Build and load a date dimension table (dim_date) with SQL](https://github.com/plainfoldhq/date-dimension/blob/main/docs/date-dimension-table-sql.md)

## Free sample data

| File | Contents |
|---|---|
| `sample/dim_date_2026.csv` | Every day of 2026 with 45 date-dimension columns: date key, ISO and US week numbers, month/quarter boundaries, US federal holidays, US business day, NYSE trading day, US federal fiscal year, NRF fiscal year/period/week |
| `sample/nrf_454_fiscal_years_2020_2030.csv` | NRF-style fiscal years 2020-2030 with 53-week years marked |

## Full pack ($19, one-time)

[Buy the full pack on Polar](https://buy.polar.sh/polar_cl_dQIvyRLcbGYoTfZgVmsIENITeo4Zu2zok8JI94KfqWn?utm_source=readme&utm_medium=readme&utm_campaign=C&utm_content=date-dimension) (Polar is the merchant of record and handles sales tax). It contains:

- `dim_date` for 2000-2050 (18,628 rows, 45 columns) as CSV and SQLite
- Four precomputed fiscal calendars 2000-2050 (NRF 4-5-4; 4-4-5 and 5-4-4 ending Saturday nearest December 31; 4-4-5 ending last Saturday of September) and a fiscal-year summary table
- PostgreSQL tables + load script (tested) and a dbt seed config with column types and tests
- The build script and tests

Also sold as part of the [calendar data bundle](https://buy.polar.sh/polar_cl_HiUeTqJE1gUqHdb3OlOWb6Jml7pdq8E71O2pA4Y9iQ3?utm_source=readme&utm_medium=readme&utm_campaign=BUNDLE&utm_content=date-dimension): this pack plus the other two Plainfold calendar data packs (business days, date dimension, time zone transitions) for $35 instead of $49.

## Checks and limits

Tests confirm known NRF fiscal years (for example, fiscal 2024 = February 4 2024 to February 1 2025; 53-week years 2000, 2006, 2012, 2017, 2023, 2028) and last-Saturday-of-September fiscal years. "NRF-style" means the rule commonly published by the National Retail Federation; this project is not affiliated with or endorsed by the NRF. Companies use their own variants, so check yours. Not accounting or tax advice.

## Related
- [plainfoldhq/us-federal-calendar](https://github.com/plainfoldhq/us-federal-calendar): US federal holidays, NYSE trading days and Federal Reserve holidays as CSV/ICS (Python package `usbizdays`); [full set on Polar](https://buy.polar.sh/polar_cl_oW9ytw22HhxLxOnke3W8ibcgTXepc2hYuAEyl1gTqqB?utm_source=readme&utm_medium=readme&utm_campaign=B&utm_content=date-dimension).
- [plainfoldhq/tz-transitions](https://github.com/plainfoldhq/tz-transitions): IANA time zone transitions 1970-2050 and DST test vectors.
- [plainfoldhq/stock-exchange-holidays](https://github.com/plainfoldhq/stock-exchange-holidays): free CSV of holidays, early closes and trading hours for nine stock exchanges (NYSE, LSE, TSX, Xetra, Euronext, Tokyo, HKEX, ASX, SIX), 2026-2028.
- [plainfoldhq/world-public-holidays](https://github.com/plainfoldhq/world-public-holidays): free CSV of public holidays for 26 countries and regions, 2026-2028, cross-checked against two independent implementations.
- [plainfoldhq/fx-settlement-holidays](https://github.com/plainfoldhq/fx-settlement-holidays): FX settlement holidays (USD, EUR/TARGET2, GBP, JPY, AUD, NZD) and T+2 spot value dates, 2026-2028, checked against QuantLib.
- All Plainfold data packs in one yearly plan: [All-Access](https://buy.polar.sh/polar_cl_xydfuofU72fdp6xSOHFtihAuniUFagYOwR9zf2M03Gl?utm_source=readme&utm_medium=readme&utm_campaign=ALLACCESS&utm_content=date-dimension).

## License

Code: MIT. Sample data: CC0 1.0. Made by Plainfold, with AI assistance. Questions: plainfoldhq@proton.me.
