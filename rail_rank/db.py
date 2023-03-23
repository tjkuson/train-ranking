"""Database functions for the train app."""
import logging
import sqlite3
from pathlib import Path

import click
import pandas as pd
from flask import Flask, current_app, g


def get_db() -> sqlite3.Connection:
    """Get the database connection."""
    # g is a special object unique to each request used to store data
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


def close_db(exc: None | Exception = None) -> None:
    """Close the database connection."""
    if exc:
        logging.exception("Database connection closed due to exception.", exc_info=exc)
    db = g.pop("db", None)
    if db is not None:
        db.close()
        logging.info("Closed database connection.")


def init_db() -> None:
    """Create tables if missing."""
    db = get_db()

    with current_app.open_resource("schema.sql") as file:
        sql_script = file.read().decode("utf8")
        db.executescript(sql_script)


@click.command("init-db")
def init_db_command() -> None:
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def load_ppm_data(csv_file: Path) -> pd.DataFrame:
    """Load data from CSV file.

    CSV file should have the following columns:
    - name
    - performance
    - date
    - time
    """
    column_names = ["name", "ppm", "record_date", "record_time"]
    ppm_df = pd.read_csv(csv_file, names=column_names)
    # If we have multiple records for a given operator on a given day, take the latest
    ppm_df = ppm_df.sort_values("record_time", ascending=False).drop_duplicates(
        subset=["name", "record_date"], keep="first"
    )
    # Check each operator has only one record per day
    if ppm_df.groupby(["name", "record_date"]).size().max() != 1:
        msg = "Multiple records per day for some operators even after cleaning."
        raise ValueError(msg)
    return ppm_df


def save_ppm_data() -> None:
    """Save data from CSV file to database."""
    csv_file = Path(__file__).parent / "train_data.csv"
    try:
        ppm_df = load_ppm_data(csv_file)
    except FileNotFoundError:
        msg = "Train data CSV file not found when trying to save data to database."
        raise FileNotFoundError(msg) from None

    db = get_db()
    cursor = db.cursor()
    operators = ppm_df["name"].unique()
    # Check all operators are in the operator table of the database
    for operator in operators:
        cursor.execute("SELECT * FROM operator WHERE name = ?", (operator,))
        if not cursor.fetchone():
            # If not, add them
            cursor.execute("INSERT INTO operator (name) VALUES (?)", (operator,))
            logging.info(
                "Added {new_operator} to the operator table",
                extra={"new_operator": operator},
            )
    # Create operator name to id mapping
    cursor.execute("SELECT * FROM operator")
    operator_id_map = {row["name"]: row["id"] for row in cursor.fetchall()}
    # Swap the operator name for the operator id
    ppm_df["operator_id"] = ppm_df["name"].map(operator_id_map)
    ppm_df = ppm_df.drop(columns=["name"])
    # If any values are missing, drop the entire row
    ppm_df = ppm_df.dropna()
    # Save the data to the database under performance table
    ppm_df.to_sql("performance", db, if_exists="append", index=False)
    db.commit()
    logging.info("Saved data to database.")
    # Delete the CSV file
    csv_file.unlink()
    logging.info("Deleted CSV file.")


@click.command("save-ppm-data")
def save_ppm_data_command() -> None:
    """Save data from CSV file to database."""
    save_ppm_data()
    click.echo("Saved data from CSV file to database.")


def prune_database() -> None:
    """Delete records so that each operator has only one record per day (the latest)."""
    db = get_db()
    cursor = db.cursor()
    # Check if there are any operators with multiple records per day
    cursor.execute(
        """
        SELECT name, record_date, COUNT(*) AS count
        FROM performance
        JOIN operator ON performance.operator_id = operator.id
        GROUP BY name, record_date
        HAVING count > 1
        """
    )
    rows = cursor.fetchall()
    if not rows:
        logging.info("No operators with multiple records per day.")
        return
    # If so, delete all but the latest record for each operator on each day
    for row in rows:
        cursor.execute(
            """
            DELETE FROM performance
            WHERE operator_id = (
                SELECT id FROM operator WHERE name = ?
            )
            AND record_date = ?
            AND TIME(record_time) < (
                SELECT MAX(TIME(record_time))
                FROM performance
                WHERE operator_id = (
                    SELECT id FROM operator WHERE name = ?
                )
                AND record_date = ?
            )
            """,
            (row["name"], row["record_date"], row["name"], row["record_date"]),
        )
    # Check there are no operators with multiple records per day
    cursor.execute(
        """
        SELECT name, record_date, COUNT(*) AS count
        FROM performance
        JOIN operator ON performance.operator_id = operator.id
        GROUP BY name, record_date
        HAVING count > 1
        """
    )
    rows = cursor.fetchall()
    if rows:
        msg = "Failed to delete records so that each operator has only one record per day."
        raise RuntimeError(msg)
    db.commit()
    logging.info("Deleted records so that each operator has only one record per day.")


@click.command("prune-database")
def prune_database_command() -> None:
    """Delete records so that each operator has only one record per day (the latest)."""
    prune_database()
    click.echo("Deleted records so that each operator has only one record per day.")


def init_app(app: Flask) -> None:
    """Register database functions with a given Flask app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(save_ppm_data_command)
    app.cli.add_command(prune_database_command)
