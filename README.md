# RailRank

> Rank train operators based on their punctuality.

Note: this is a work in progress.

## Motivation

I wanted to see which train operators were the most punctual in the United Kingdom. Each network has a monopoly on its own lines, so direct competition and comparisons are not possible. Nonetheless, it is still fun to compare.

## Features

- Fetches data from the Network Rail API
- Displays PPM data in a table using Flask
- Saves data to an SQLite database

More features to come. If you have any suggestions, please open an issue.

## Usage

Clone or fork this repository, run the container and start developing.

    docker-compose up

Or if you prefer `podman`:

    podman-compose up

You should now be able to access the application at [http://localhost:5000](http://localhost:5000) or else at the port you specified in the `compose.yml` file.

You will have to create a `constants.py` file in the `app` directory with the following content:

```python
# Path: app/constants.py
username: str = ...
password: str = ...
flask_secret_key: str | bytes = ...
```

The username and password are the ones you use to log in to the Network Rail API. The Flask secret key is used to encrypt the session cookie and other security-related things.

To run app commands, execute:

    flask --app train_app <command>

Here are some examples:

    flask --app train_app init-db
    flask --app train_app save-ppm-data
    flask --app train_app prune-database

## Develop

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please update tests as appropriate.

Install the development dependencies:

    pip install -r requirements-dev.txt

## Authors

RailRank was created by Tom Kuson ([@tjkuson](https://github.com/tjkuson)).

## Licence

RailRank is released under the [AGPL version 3](LICENCE).

## Acknowledgements

- The [Open Rail Data Wiki](https://wiki.openraildata.com/) contributors
- The [Network Rail open data platform](https://publicdatafeeds.networkrail.co.uk/)
- Rail workers
