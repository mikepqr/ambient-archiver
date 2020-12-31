import glob

import pandas as pd

DATA_DIR = "data/"


def load_data():
    jsonfiles = glob.glob(DATA_DIR + "*.json.gz")
    df = pd.concat(pd.read_json(jsonfile) for jsonfile in jsonfiles)
    df.index = pd.to_datetime(df.date)
    df.index = df.index.tz_convert("US/Pacific")
    df = df.sort_index()
    df = df[~df.duplicated()]
    return df
