import logging

import click

from ambient.ambient import make_context
from ambient.ambient import today as _today
from ambient.ambient import yesterday as _yesterday
from ambient.backfill import backfill as _backfill


@click.group()
@click.version_option()
@click.option("--quiet", "-q", help="Be quiet", is_flag=True, default=False)
@click.option("--application-key", required=True)
@click.option("--api-key", required=True)
@click.option("--mac", required=True)
@click.pass_context
def cli(ctx, quiet, application_key, api_key, mac):
    if quiet:
        logging.basicConfig(level=logging.WARN, format="%(message)s")
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s")
    auth_data = {
        "application_key": application_key,
        "api_key": api_key,
        "mac": mac,
    }
    ctx.obj = make_context(auth_data)


@cli.command()
@click.pass_obj
def today(context):
    _today(context)


@cli.command()
@click.pass_obj
def yesterday(context):
    _yesterday(context)


@cli.command()
@click.pass_obj
def backfill(context):
    _backfill(context)


def main():
    cli(auto_envvar_prefix="AMBIENT")
