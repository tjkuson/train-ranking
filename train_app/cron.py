"""Cron job to save data to database."""
import logging
import sqlite3
from pathlib import Path

import pandas as pd


def create_db() -> None:
    """Create database from schema."""
    schema_path = Path(__file__).parent / "schema.sql"
    db_path = Path(__file__).parent / "train.db"
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        with open(schema_path) as file:
            cursor.executescript(file.read())
        conn.commit()


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


def save_ppm_data(csv_file: Path) -> None:
    """Save data from CSV file to database."""
    ppm_df = load_ppm_data(csv_file)

    if not csv_file.exists():
        msg = f"CSV file {csv_file} not found"
        raise FileNotFoundError(msg)

    db_path = Path(__file__).parent / "train.db"
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
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
        operator_map = {row[1]: row[0] for row in cursor.fetchall()}
        # Add the operator ID to the dataframe
        ppm_df["operator_id"] = ppm_df["name"].map(operator_map)
        # Drop the operator name column
        ppm_df = ppm_df.drop("name", axis=1)
        # If any values are missing, drop the entire row
        ppm_df = ppm_df.dropna()
        # Save the dataframe to the database under performance table
        ppm_df.to_sql("performance", conn, if_exists="append", index=False)
        conn.commit()
        logging.info("Saved %s rows to the database", len(ppm_df.index))
        # Delete the CSV file
        csv_file.unlink()
        logging.info("Deleted %s", csv_file)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    create_db()
    csv_path = Path(__file__).parent / "train_data.csv"
    save_ppm_data(csv_path)
