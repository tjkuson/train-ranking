"""Page blueprint."""
from flask import Blueprint, render_template

bp = Blueprint("page", __name__)


@bp.route("/")
def index() -> str:
    """Render the index page."""
    return render_template("page/index.html")
