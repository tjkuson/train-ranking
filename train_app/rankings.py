"""Rankings blueprint."""
from flask import (
    Blueprint,
    render_template,
)

from train_app.db import get_db

bp = Blueprint("rankings", __name__, url_prefix="/")


@bp.route("/")
def index() -> str:
    """Show rankings."""
    db = get_db()
    # Join the performance and operators on performance.operator_id = operators.id
    rankings = db.execute(
        "SELECT operator.name, AVG(performance.ppm) AS ppm"
        " FROM performance JOIN operator ON performance.operator_id = operator.id"
        " GROUP BY operator.name"
        " ORDER BY ppm DESC"
    ).fetchall()
    return render_template("rankings/index.html", rankings=rankings)
