# ambient-archiver

Download and analyse your data from ambientweather.net

## Installation

    pip install ambient-archiver

This installs `ambient` in your PATH.

## Usage

`ambient` takes three required options: `--api_key`, `--application_key` and
`--mac`, which you can get from your [account page on
ambientweather.net](https://ambientweather.net/account). You can omit the
options by setting `AMBIENT_API_KEY` `AMBIENT_APPLICATION_KEY` and `AMBIENT_MAC`
in your environment.

See `ambient --help` for more.

### Commands

 - `ambient backfill` writes all data from 2020-01-01 to the end of the last
   UTC day into YYYY-MM-DD.json.gz files in the present working directory (one
   file per day)

 - `ambient today` overwrites <today>.json.gz with all data since 00:00 UTC

 - `ambient yesterday` overwrites <yesterday>.json.gz with all data between
   00:00 UTC yesterday and 23:59 UTC yesterday.

`backfill` does not overwrite files. You must manually delete them if
you want fresh copies for some reason. `today` and `yesterday` overwrite.

### Shell completion

You can optionally enable shell completion by running the appropriate command
for your shell:

```bash
eval "$(_AMBIENT_COMPLETE=bash_source ambient)" >> ~/.bashrc # bash
eval "$(_AMBIENT_COMPLETE=zsh_source ambient)" >> ~/.zshrc  # zsh
_AMBIENT_COMPLETE=fish_source foo-bar > ~/.config/fish/completions/ambient.fish  # fish
```

## Automation with Github Actions

1. Create a new repository, run `ambient backfill` then check everything in
2. Add these files in `.github/workflows/`

   <details>

   <summary><code>.github/workflows/ambient.yml</code> (<code>ambient today</code>
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
                pip install ambient-archiver
            - name: Overwrite since midnight
              env:
                AMBIENT_MAC: ${{ secrets.AMBIENT_MAC }}
                AMBIENT_API_KEY: ${{ secrets.AMBIENT_API_KEY }}
                AMBIENT_APPLICATION_KEY: ${{ secrets.AMBIENT_APPLICATION_KEY }}
              run: ambient today
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

   <summary><code>.github/workflows/daily.yml</code> (<code>ambient yesterday</code>
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
                pip install ambient-archiver
            - name: Overwrite yesterday
              env:
                AMBIENT_MAC: ${{ secrets.AMBIENT_MAC }}
                AMBIENT_API_KEY: ${{ secrets.AMBIENT_API_KEY }}
                AMBIENT_APPLICATION_KEY: ${{ secrets.AMBIENT_APPLICATION_KEY }}
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
4. Configure `AMBIENT_MAC`, `AMBIENT_API_KEY` and `AMBIENT_APPLICATION_KEY` as
   Secrets in the GitHub settings for that repository
