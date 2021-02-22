# ambient-archiver

Download and analyse your data from ambientweather.net

## Installation

    pip install git+https://github.com/mikepqr/ambient-archiver.git

## Usage

Export `MAC`, `API_KEY` and `APPLICATION_KEY` then run:

 - `ambient-backfill` to write all data from 2020-01-01 to the end of the last
   UTC day into YYYY-MM-DD.json.gz files in the present working directory (one
   file per day)

 - `ambient-osm` to Overwrite Since Midnight, i.e. (over)write data since the
   end of the previous UTC day into today's json.gz file.

 - `ambient-oy` to Overwrite Yesterday, i.e. (over)write data during the last
    the previous UTC day into yesterday's json.gz file.

`ambient-backfill` does not overwrite files. You must manually delete them if
you want fresh copies for some reason. `ambient-osm` and `ambient-oy` overwrite.

## Analysis

`ambient.loaddf()` returns a Pandas dataframe of all data in the working
directory.

## Automation with Github Actions

1. Create a new repository, run `ambient-backfill` then check everything in
2. Add these files in `.github/workflows/`

   <details>

   <summary><code>.github/workflows/ambient.yml</code> (<code>ambient-osm</code>
   every five minutes)</summary>

        name: ambient

        on:
          workflow_dispatch:
          # every 5 minutes
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

   </details>

   <details>

   <summary><code>.github/workflows/daily.yml</code> (<code>ambient-oy</code>
   every day at 01:00 UTC)</summary>

        name: daily

        on:
          workflow_dispatch:
          # daily, 1am UTC
          schedule:
            - cron:  '0 1 * * *'

        jobs:
          daily:
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
            - name: Overwrite yesterday
              env:
                MAC: ${{ secrets.MAC }}
                API_KEY: ${{ secrets.API_KEY }}
                APPLICATION_KEY: ${{ secrets.APPLICATION_KEY }}
              run: ambient-oy
            - name: Commit and push if it changed
              run: |-
                git config --global user.name "scraper-bot"
                git config user.email "actions@users.noreply.github.com"
                git add -A
                timestamp=$(date -u)
                git commit -m "Downloaded at at ${timestamp}" || exit 0
                git push
   </details>

   The daily workflow deals with the fact that the more regular job does not
   in practice run every five minutes. It ensures the completed file for that
   day has the last few records for the day.

3. Push to GitHub
4. Configure `MAC`, `API_KEY` and `APPLICATION_KEY` as Secrets in the GitHub
   settings for that repository
