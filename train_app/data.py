"""Module to fetch data from the STOMP server."""
from __future__ import annotations

import json
import logging
import socket
import sys
import time
from csv import writer
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import stomp

from train_app import constants


# stomp doesn't have stubs for the ConnectionListener so thinks this subclasses Any
class StompClient(stomp.ConnectionListener):  # type: ignore[misc]
    """Class to handle the STOMP connection."""

    def on_heartbeat(self: StompClient) -> None:
        """Log when a heartbeat is received from the server."""
        logging.info("Received a heartbeat")

    def on_heartbeat_timeout(self: StompClient) -> None:
        """Log when a heartbeat is not received from the server."""
        logging.error("Heartbeat timeout")

    def on_error(self: StompClient, frame: stomp.utils.Frame) -> None:
        """Log when an error is received from the server."""
        msg = frame.headers.get("message")
        logging.error(msg)

    def on_disconnected(self: StompClient) -> None:
        """Log, warn, and exit when the connection is disconnected."""
        reconnect_delay_secs = 15
        logging.warning(
            "Disconnected - waiting %s seconds before exiting",
            reconnect_delay_secs,
        )
        time.sleep(reconnect_delay_secs)
        logging.warning("Exiting")
        sys.exit(-1)

    def on_connecting(self: StompClient, host_and_port: tuple[str, int]) -> None:
        """Log when the connection is being established."""
        logging.info("Connecting to %s", extra={"host_port": host_and_port[0]})

    def on_message(self: StompClient, frame: stomp.utils.Frame) -> None:
        """Parse data when a message is received from the server."""
        try:
            message = json.loads(frame.body)["RTPPMDataMsgV1"]
            train_data_csv = Path(__file__).parent / "train_data.csv"
            with open(train_data_csv, "a") as file:
                ppm_data = self.get_ppm(message)
                # Save each dict item on a new line
                for item in ppm_data:
                    logging.info(
                        "Logging data for %s: ppm=%s, date=%s, time=%s",
                        item["name"],
                        item["ppm"],
                        item["date"],
                        item["time"],
                    )
                    csv_writer = writer(file)
                    csv_writer.writerow(item.values())

        except Exception as exc:
            logging.exception("Error parsing message", exc_info=exc)
        else:
            logging.info("Message received and parsed successfully")

    @staticmethod
    def parse_operator_data(operator_data: dict[str, Any]) -> dict[str, str]:
        """Parse the data from the JSON message."""
        return {
            "name": operator_data["name"],
            "ppm": operator_data["PPM"]["text"],
        }

    @staticmethod
    def get_timestamp(rtppm_data: dict[str, Any]) -> dict[str, str]:
        """Get the timestamp from the JSON message."""
        unix_timestamp = rtppm_data["RTPPMData"]["snapshotTStamp"]
        # National Rail uses milliseconds, so divide by 1000
        ppm_dt = datetime.fromtimestamp(int(unix_timestamp) / 1000, tz=timezone.utc)
        ppm_date, ppm_time = str(ppm_dt).split(" ")
        return {"date": ppm_date, "time": ppm_time}

    def get_ppm(self: StompClient, rtppm_data: dict[str, Any]) -> list[dict[str, str]]:
        """Get the PPM data from the JSON message."""
        timestamp = self.get_timestamp(rtppm_data)
        operators = rtppm_data["RTPPMData"]["NationalPage"]["Operator"]
        return [
            self.parse_operator_data(operator) | timestamp for operator in operators
        ]


class DataFetcher:
    """Class to fetch data from the STOMP server."""

    def __init__(self: DataFetcher) -> None:
        """Initialise the DataFetcher class."""
        self.hostname = "publicdatafeeds.networkrail.co.uk"
        self.port = 61618
        self.username = constants.username
        self.password = constants.password
        self.topic = "/topic/RTPPM_ALL"
        self.hearbeat_interval_ms = 15000

    def connect_and_subscribe(self: DataFetcher) -> None:
        """Connect to the STOMP server and subscribe to the topic."""
        conn = stomp.Connection12(
            [(self.hostname, self.port)],
            auto_decode=False,
            heartbeats=(self.hearbeat_interval_ms, self.hearbeat_interval_ms),
        )
        conn.set_listener("", StompClient())
        client_id = socket.getfqdn()
        connect_header = {"client-id": self.username + "-" + client_id}
        subscribe_header = {"activemq.subscriptionName": client_id}
        conn.connect(
            username=self.username,
            passcode=self.password,
            wait=True,
            headers=connect_header,
        )
        conn.subscribe(
            destination=self.topic,
            id=1,
            ack="auto",
            headers=subscribe_header,
        )

        # Wait forever
        while True:
            time.sleep(1)

        conn.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fetcher = DataFetcher()
    fetcher.connect_and_subscribe()
