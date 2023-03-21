"""Monitor trains."""
import os
from contextlib import suppress

from flask import Flask

from . import constants


def create_app(test_config=None) -> Flask:
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

    # Add the about page
    from . import about

    app.register_blueprint(about.bp)
    app.add_url_rule("/about", endpoint="about")

    return app
