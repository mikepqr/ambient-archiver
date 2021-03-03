import gzip
import json
import logging
import math
import os
import time
from datetime import datetime, timedelta, timezone

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

REST_API_BASE = "https://api.ambientweather.net/v1"
RETRIES = 5
BACKOFF_FACTOR = 1
STATUS_FORCELIST = [401, 413, 429, 503]  # defaults + 401 for flaky API
LIMIT = 288


def make_context(auth_data=None):
    # https://www.peterbe.com/plog/best-practice-with-retries-with-requests
    if not auth_data:
        auth_data = {
            "api_key": os.environ["API_KEY"],
            "application_key": os.environ["APPLICATION_KEY"],
            "mac": os.environ["MAC"],
        }
    s = requests.Session()
    s.params = {
        "apiKey": auth_data["api_key"],
        "applicationKey": auth_data["application_key"],
        "limit": LIMIT,
    }
    retry = Retry(
        total=RETRIES,
        read=RETRIES,
        connect=RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        status_forcelist=STATUS_FORCELIST,
    )
    adapter = HTTPAdapter(max_retries=retry)
    s.mount(REST_API_BASE, adapter)
    return {"session": s, "mac": auth_data["mac"]}


def last_midnight_utc():
    """Returns a datetime for the most recent 23:59 UTC."""
    ago_24h = datetime.now(tz=timezone.utc) - timedelta(days=1)
    return datetime(
        ago_24h.year, ago_24h.month, ago_24h.day, 23, 59, tzinfo=timezone.utc
    )


def now_utc():
    return datetime.now(tz=timezone.utc)


def getdata(end: datetime, start=None, context=None):
    """Get records from start to end. Gets previous 24 hours if start is None."""
    time.sleep(1.1)  # < 1 request per second
    params = {"endDate": end.isoformat()}
    if start:
        five_min_intervals = math.ceil((end - start).total_seconds() / (5 * 60))
        params["limit"] = str(five_min_intervals)
    if not context:
        context = make_context()
    r = context["session"].get(
        f"{REST_API_BASE}/devices/{context['mac']}",
        params=params,
    )
    r.raise_for_status()
    return r.json()


def log_head_tail(data):
    try:
        logging.info(
            f"Got {len(data)} records from {data[-1]['date']} to {data[0]['date']}"
        )
    except KeyError:
        logging.info(f"{data}")
        raise ValueError("Data format invalid. Check api_key, application_key and mac.")


def today(context=None):
    """Overwrite <today>.json.gz with all data since 00:00 UTC"""
    start = last_midnight_utc()
    end = now_utc()
    data = getdata(end=end, start=start, context=context)
    prettydate = f"{end.date().isoformat()}"
    log_head_tail(data)
    with gzip.open(prettydate + ".json.gz", "wt", encoding="ascii") as f:
        f.write(json.dumps(data))


def yesterday(context=None):
    """Overwrite <yesterday>.json.gz with data from 00:00 to 23:59 UTC"""
    end = last_midnight_utc()
    data = getdata(end=end, context=context)
    prettydate = f"{end.date().isoformat()}"
    log_head_tail(data)
    with gzip.open(prettydate + ".json.gz", "wt", encoding="ascii") as f:
        f.write(json.dumps(data))
