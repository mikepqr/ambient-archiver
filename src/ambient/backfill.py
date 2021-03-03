import glob
import gzip
import json
import logging
import os
from datetime import datetime, timedelta, timezone

from ambient.ambient import LIMIT, getdata, last_midnight_utc


def daterange(start, end, delta=timedelta(days=1)):
    """Yield all datetimes from start to end (inclusive) with interval delta."""
    dt = start
    while min(start, end) <= dt <= max(start, end):
        yield dt
        dt += delta


def checklength():
    for jgz in sorted(glob.glob("*.json.gz")):
        with gzip.open(jgz, "rt", encoding="ascii") as f:
            data = json.load(f)
            if len(data) != 288:
                print(f"Got {len(data):>3d} records for {jgz}. Expected {LIMIT}")


def backfill(context=None, end=datetime(2020, 1, 1, tzinfo=timezone.utc)):
    """Backfills data from enddt to the most recent midnight UTC."""
    start = last_midnight_utc()
    for dt in daterange(start, end, delta=timedelta(days=-1)):
        prettydate = f"{dt.date().isoformat()}"
        if os.path.exists(prettydate + ".json.gz"):
            logging.warning(f"Skipping {prettydate}. File exists")
        else:
            data = getdata(dt, context=context)
            if len(data) != 288:
                logging.warning(
                    f"Got {len(data)} records for {prettydate}. Expected {LIMIT}"
                )
            with gzip.open(prettydate + ".json.gz", "wt", encoding="ascii") as f:
                f.write(json.dumps(data))
