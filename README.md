# ambient (WIP)

Code to monitor, visualize and download data from the ambient weather API.

So far:

 - export `MAC`, `API_KEY` and `APPLICATION_KEY`
 - `python backfill.py` to download data from 2020-01-01 to 2020-01-28 to daily
   json.gz files in `./data`.

Coming next:

 - `poll.py` to be run as a recurring job to download new data
 - visualization and analysis
