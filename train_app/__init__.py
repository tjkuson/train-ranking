"""Monitor trains."""
import os
from collections.abc import Mapping
from contextlib import suppress
from typing import Any

from flask import Flask

from train_app import constants


def create_app(test_config: None | Mapping[str, Any] = None) -> Flask:
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=constants.flask_secret_key,
        DATABASE=os.path.join(app.instance_path, "train.db"),
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure instance folder exists
    with suppress(OSError):
        os.makedirs(app.instance_path)

    # Add the database functions
    from . import db

    db.init_app(app)

    # Add the rankings page
    from . import rankings

    app.register_blueprint(rankings.bp)

    # Add the about page
    from . import about

    app.register_blueprint(about.bp)
    app.add_url_rule("/about", endpoint="about")

    return app
