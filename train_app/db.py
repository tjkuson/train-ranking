"""Database functions for the train app."""
import sqlite3

import click
from flask import Flask, current_app, g


def get_db() -> sqlite3.Connection:
    """Get the database connection."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Return rows that behave like dicts
        g.db.row_factory = sqlite3.Row
    if not g.db:
        msg = "No database connection"
        raise RuntimeError(msg)
    if not isinstance(g.db, sqlite3.Connection):
        msg = "Database connection is not a sqlite3.Connection"
        raise TypeError(msg)
    return g.db


def close_db(e: bool = None) -> None:  # TODO: What is e?
    """Close the database connection."""
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db() -> None:
    """Create tables if missing."""
    db = get_db()

    with current_app.open_resource("schema.sql") as file:
        db.executescript(file.read().decode("utf8"))


@click.command("init-db")
def init_db_command() -> None:
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app: Flask) -> None:
    """Register database functions with the Flask app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
