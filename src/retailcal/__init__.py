#!/usr/bin/env python3
"""52/53-week retail and fiscal calendars (4-4-5, 4-5-4, 5-4-4) - any variant.

Python 3 standard library only. MIT license.

A 52/53-week fiscal year always ends on the same weekday. Two common rules:
  nearest: the year ends on that weekday NEAREST a month's last day
           (NRF retail calendar: Saturday nearest January 31)
  last:    the year ends on the LAST such weekday of the month
The 13 weeks of each quarter are split into periods by the pattern
(4-4-5, 4-5-4 or 5-4-4). In a 53-week year the extra week goes to the last
period of the year (NRF practice), unless --extra-week-period says otherwise.

Fiscal year naming: "start" = named by the calendar year in which it starts
(NRF: fiscal 2025 = Feb 2 2025 - Jan 31 2026); "end" = by the year it ends.
For a December end month both namings give the same label: the calendar year
the fiscal year ends in (it starts in the last days of the previous December).

CLI:
  retailcal --preset nrf-454 --from 2000 --to 2050 > nrf.csv
  retailcal --end-month 9 --weekday sat --rule last --pattern 445 \
      --naming end --from 2010 --to 2040 > fy.csv
  retailcal --preset nrf-454 --year-table      # one row per fiscal year
"""
import argparse
import csv
import sys
from datetime import date, timedelta

WEEKDAYS = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
PATTERNS = {"445": (4, 4, 5), "454": (4, 5, 4), "544": (5, 4, 4)}
PRESETS = {
    # name: (end_month, weekday, rule, pattern, naming)
    "nrf-454": (1, "sat", "nearest", "454", "start"),
    "445-sat-nearest-dec": (12, "sat", "nearest", "445", "end"),
    "445-sat-last-sep": (9, "sat", "last", "445", "end"),
    "544-sat-nearest-dec": (12, "sat", "nearest", "544", "end"),
}

COLUMNS = ["date", "fiscal_year", "fiscal_quarter", "fiscal_period", "fiscal_week",
           "week_of_period", "day_of_fiscal_year", "day_of_fiscal_week",
           "fiscal_year_start", "fiscal_year_end", "period_start", "period_end",
           "week_start", "week_end", "weeks_in_year", "is_53_week_year"]


class Calendar:
    def __init__(self, end_month, weekday, rule="nearest", pattern="454", naming="start",
                 extra_week_period=12):
        if rule not in ("nearest", "last"):
            raise ValueError("rule must be nearest or last")
        if naming not in ("start", "end"):
            raise ValueError("naming must be start or end")
        if not (isinstance(end_month, int) and 1 <= end_month <= 12):
            raise ValueError("end_month must be 1-12")
        if not (isinstance(extra_week_period, int) and 1 <= extra_week_period <= 12):
            raise ValueError("extra_week_period must be 1-12")
        if isinstance(weekday, str) and weekday.lower() not in WEEKDAYS:
            raise ValueError("weekday must be one of %s" % ", ".join(WEEKDAYS))
        if isinstance(pattern, str) and pattern not in PATTERNS:
            raise ValueError("pattern must be 445, 454 or 544")
        self.end_month = end_month
        self.weekday = WEEKDAYS[weekday.lower()] if isinstance(weekday, str) else weekday
        self.rule = rule
        self.pattern = PATTERNS[pattern] if isinstance(pattern, str) else tuple(pattern)
        self.naming = naming
        self.extra_week_period = extra_week_period

    def _month_end(self, y):
        m = self.end_month
        return date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1)

    def year_end_in(self, y):
        """Fiscal year-end date anchored on the end month of calendar year y."""
        me = self._month_end(y)
        back = (me.weekday() - self.weekday) % 7  # days back to the last such weekday
        last = me - timedelta(days=back)
        if self.rule == "last" or back <= 3:
            return last
        return last + timedelta(days=7)

    def _anchor_year(self, fy):
        """Calendar year (of the end month) in which fiscal year `fy` ends."""
        if self.naming == "end":
            return fy
        # "start" naming: fy starts in calendar year fy, ends ~12 months later.
        return fy + 1 if self.end_month < 12 else fy

    def bounds(self, fy):
        end = self.year_end_in(self._anchor_year(fy))
        prev_end = self.year_end_in(self._anchor_year(fy) - 1)
        return prev_end + timedelta(days=1), end

    def fiscal_year_of(self, d):
        guess = d.year if self.naming == "end" else d.year - (1 if self.end_month < 12 else 0)
        for fy in (guess - 1, guess, guess + 1, guess + 2):
            s, e = self.bounds(fy)
            if s <= d <= e:
                return fy
        raise AssertionError("no fiscal year found for %s" % d)

    def period_lengths(self, fy):
        s, e = self.bounds(fy)
        weeks = ((e - s).days + 1) // 7
        lens = list(self.pattern) * 4
        if weeks == 53:
            lens[self.extra_week_period - 1] += 1
        return lens, weeks

    def row(self, d):
        fy = self.fiscal_year_of(d)
        s, e = self.bounds(fy)
        lens, weeks = self.period_lengths(fy)
        doy = (d - s).days + 1
        wk = (doy - 1) // 7 + 1
        acc, period = 0, 0
        for i, n in enumerate(lens):
            if wk <= acc + n:
                period = i + 1
                break
            acc += n
        p_start = s + timedelta(weeks=acc)
        p_end = p_start + timedelta(weeks=lens[period - 1]) - timedelta(days=1)
        w_start = s + timedelta(weeks=wk - 1)
        return {
            "date": d.isoformat(), "fiscal_year": fy, "fiscal_quarter": (period - 1) // 3 + 1,
            "fiscal_period": period, "fiscal_week": wk, "week_of_period": wk - acc,
            "day_of_fiscal_year": doy, "day_of_fiscal_week": (doy - 1) % 7 + 1,
            "fiscal_year_start": s.isoformat(), "fiscal_year_end": e.isoformat(),
            "period_start": p_start.isoformat(), "period_end": p_end.isoformat(),
            "week_start": w_start.isoformat(), "week_end": (w_start + timedelta(days=6)).isoformat(),
            "weeks_in_year": weeks, "is_53_week_year": int(weeks == 53),
        }

    def rows(self, fy_from, fy_to):
        for fy in range(fy_from, fy_to + 1):
            s, e = self.bounds(fy)
            d = s
            while d <= e:
                yield self.row(d)
                d += timedelta(days=1)

    def year_rows(self, fy_from, fy_to):
        for fy in range(fy_from, fy_to + 1):
            s, e = self.bounds(fy)
            lens, weeks = self.period_lengths(fy)
            yield {"fiscal_year": fy, "fiscal_year_start": s.isoformat(), "fiscal_year_end": e.isoformat(),
                   "weeks": weeks, "period_weeks": "-".join(map(str, lens))}


def from_args(a):
    if a.preset:
        m, wd, rule, pat, naming = PRESETS[a.preset]
    else:
        m, wd, rule, pat, naming = a.end_month, a.weekday, a.rule, a.pattern, a.naming
    return Calendar(m, wd, rule, pat, naming, a.extra_week_period)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--preset", choices=sorted(PRESETS))
    ap.add_argument("--end-month", type=int, default=1)
    ap.add_argument("--weekday", choices=sorted(WEEKDAYS), default="sat")
    ap.add_argument("--rule", choices=["nearest", "last"], default="nearest")
    ap.add_argument("--pattern", choices=sorted(PATTERNS), default="454")
    ap.add_argument("--naming", choices=["start", "end"], default="start")
    ap.add_argument("--extra-week-period", type=int, default=12)
    ap.add_argument("--from", dest="fy_from", type=int, default=2000)
    ap.add_argument("--to", dest="fy_to", type=int, default=2050)
    ap.add_argument("--year-table", action="store_true")
    a = ap.parse_args(argv)
    try:
        cal = from_args(a)
    except ValueError as e:
        ap.error(str(e))
    w = csv.writer(sys.stdout, lineterminator="\n")
    if a.year_table:
        cols = ["fiscal_year", "fiscal_year_start", "fiscal_year_end", "weeks", "period_weeks"]
        w.writerow(cols)
        for r in cal.year_rows(a.fy_from, a.fy_to):
            w.writerow([r[c] for c in cols])
    else:
        w.writerow(COLUMNS)
        for r in cal.rows(a.fy_from, a.fy_to):
            w.writerow([r[c] for c in COLUMNS])


if __name__ == "__main__":
    main()
