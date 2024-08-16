#!/usr/bin/env python3
import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime
from os import error
from pathlib import Path

parser = argparse.ArgumentParser(
    description="Create csv report from Entra AD interactive sign-in 'entra.microsoft.com' Identity > Monitoring & health > Sign-in logs"
)
parser.add_argument(
    "file",
    type=str,
    help="Report file.json, eg. 'InteractiveSignIns_2024-01-11_2024-02-10.json'",
)
parser.add_argument(
    "-d",
    "--delta-date",
    type=str,
    default=str(datetime.now().date()),
    help="Last date for counting delta, default is today in format: '%(default)s'",
)
_args = parser.parse_args()
FILE, DELTA_DATE = _args.file, _args.delta_date


def parse_login_data(_data: dict) -> list[tuple[str, str]]:
    """return userPrincipalName and last logon"""
    selected_data = defaultdict(list)
    for i in _data:
        user: str = i["userPrincipalName"]
        aut_date: list[str] = [
            j["authenticationStepDateTime"] for j in i["authenticationDetails"]
        ]
        selected_data[user] += aut_date

    user_last_login = {
        #'2024-01-11T13:58:34Z' -> datetime.datetime(2024, 1, 11, 13, 58, 34)
        # last login date
        k: sorted(v, key=lambda d: datetime.strptime(d, "%Y-%m-%dT%H:%M:%SZ"))[-1]
        for k, v in selected_data.items()
    }
    sorted_data: list[tuple] = sorted(
        # sort users by last login
        user_last_login.items(),
        key=lambda x: datetime.strptime(x[1], "%Y-%m-%dT%H:%M:%SZ"),
    )

    def _get_days_since_last_login(last_date: str) -> int:
        _last_date = datetime.strptime(last_date, "%Y-%m-%dT%H:%M:%SZ").date()
        delta = datetime.strptime(DELTA_DATE, "%Y-%m-%d").date() - _last_date
        return delta.days

    data_with_time_delta: list[tuple] = [
        (u, l, _get_days_since_last_login(l)) for u, l in sorted_data
    ]

    return data_with_time_delta


if __name__ == "__main__":
    REPORT: str = str(
        Path(FILE).parent / f"Report_{Path(FILE).name.removesuffix('.json')}.csv"
    )
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            json_data = json.loads(f.read())
        report = parse_login_data(json_data)

        with open(REPORT, "w", encoding="utf-8") as r:
            csv_out = csv.writer(r)
            csv_out.writerow(
                [
                    "User Principal Name",
                    "Date of the Last Interactive Login",
                    "Days Since Last Login",
                ]
            )
            csv_out.writerows(report)
    except error as e:
        print(e)
