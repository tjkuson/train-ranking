# Train ranking

> Rank train operators based on their punctuality.

Note: this is a work in progress.

## Usage

Clone or fork this repository, run the container and start developing.

    docker-compose up

Or if you prefer `podman`:

    podman-compose up

You should now be able to access the application at [http://localhost:5000](http://localhost:5000) or else at the port you specified in the `compose.yml` file.

You will have to create a `constants.py` file in the `app` directory with the following content:

```python
# Path: app/constants.py
username = ...
password = ...
```

The username and password are the ones you use to log in to the Network Rail API.

## Develop

Install the development dependencies:

    pip install -r requirements-dev.txt
