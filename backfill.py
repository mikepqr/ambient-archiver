import gzip
import json
import logging
import os
import time
from datetime import datetime, timedelta

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

REST_API_BASE = "https://api.ambientweather.net/v1"
RETRIES = 5
BACKOFF_FACTOR = 1
STATUS_FORCELIST = [401, 413, 429, 503]  # defaults + 401 for flaky API
LIMIT = 288
PARAMS = {
    "apiKey": os.environ["API_KEY"],
    "applicationKey": os.environ["APPLICATION_KEY"],
    "limit": LIMIT,
}


def session():
    # https://www.peterbe.com/plog/best-practice-with-retries-with-requests
    s = requests.Session()
    s.params = PARAMS
    retry = Retry(
        total=RETRIES,
        read=RETRIES,
        connect=RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        status_forcelist=STATUS_FORCELIST,
    )
    adapter = HTTPAdapter(max_retries=retry)
    s.mount(REST_API_BASE, adapter)
    return s


s = session()


def getdate(dt: datetime):
    time.sleep(1.1)  # < 1 request per second
    r = s.get(
        f"{REST_API_BASE}/devices/{os.environ['MAC']}",
        params={"endDate": dt.isoformat()},
    )
    r.raise_for_status()
    return r.json()


def daterange(start, end, delta=timedelta(days=1)):
    """
    Yield all datetimes from start to end (inclusive) with interval delta
    """
    dt = start
    while min(start, end) <= dt <= max(start, end):
        yield dt
        dt += delta


def main():
    # ask for 24 hours starting just before midnight, which seems to result in
    # more consistent return values from API
    start = datetime(2020, 12, 28, 23, 59, 59)
    # API returns no data before this
    end = datetime(2020, 1, 1)
    for dt in daterange(start, end, delta=timedelta(days=-1)):
        prettydate = f"{dt.date().isoformat()}"
        if os.path.exists("data/" + prettydate + ".json.gz"):
            logging.info(f"Skipping {prettydate}. File exists")
        else:
            data = getdate(dt)
            if len(data) != 288:
                logging.warning(
                    f"Got {len(data)} records for {prettydate}. Expected {LIMIT}"
                )
            with gzip.open(
                "data/" + prettydate + ".json.gz", "wt", encoding="ascii"
            ) as f:
                f.write(json.dumps(data))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
