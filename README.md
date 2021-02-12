# ambient-archiver

Download and analyse your data from ambientweather.net

## Installation

    pip install git+https://github.com/mikepqr/ambient-archiver.git

## Usage

Export `MAC`, `API_KEY` and `APPLICATION_KEY` then run:

 - `ambient-backfill` to write all data from 2020-01-01 to the end of the last
   UTC day into YYYY-MM-DD.json.gz files in the present working directory (one file per
   day)

 - `ambient-osm` to Overwrite Since Midnight, i.e. (over)write all data since the
   end of the last UTC day into today's json.gz file.

`ambient-backfill` will not overwrite files. You must manually delete them if
you want fresh copies for some reason.

`ambient-osm` overwrites today's file.

## Analysis

`ambient.loaddf()` returns a Pandas dataframe of all data in the working
directory.

## Automation with Github Actions

1. Create a new repository, run `ambient-backfill` then check everything in
2. Commit a file `.github/workflows/ambient.yml`

       name: ambient

       on:
         # push:
         workflow_dispatch:
         schedule:
           - cron:  '*/5 * * * *'

       jobs:
         ambient:
           runs-on: ubuntu-latest
           steps:
           - name: Check out repo
             uses: actions/checkout@v2
           - name: Set up Python
             uses: actions/setup-python@v2
             with:
               python-version: 3.8
           - name: Install Python dependencies
             run: |
               pip install git+https://github.com/mikepqr/ambient-archiver.git
           - name: Overwrite since midnight
             env:
               MAC: ${{ secrets.MAC }}
               API_KEY: ${{ secrets.API_KEY }}
               APPLICATION_KEY: ${{ secrets.APPLICATION_KEY }}
             run: ambient-osm
           - name: Commit and push if it changed
             run: |-
               git config --global user.name "scraper-bot"
               git config user.email "actions@users.noreply.github.com"
               git add -A
               timestamp=$(date -u)
               git commit -m "Scraped at ${timestamp}" || exit 0
               git push

3. Push to GitHub
4. Configure `MAC`, `API_KEY` and `APPLICATION_KEY` as Secrets in the GitHub
   settings for that repository
