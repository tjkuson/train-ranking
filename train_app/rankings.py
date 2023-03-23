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
    # Get operator average rankings in the last 7 days, 30 days, and 90 days
    rankings = db.execute(
        "SELECT operator.name, "
        "ROUND(AVG(CASE WHEN date(performance.record_date) > date('now', '-7 days') THEN performance.ppm END), 2) AS average_rating_7_days, "
        "ROUND(AVG(CASE WHEN date(performance.record_date) > date('now', '-30 days') THEN performance.ppm END), 2) AS average_rating_30_days, "
        "ROUND(AVG(CASE WHEN date(performance.record_date) > date('now', '-90 days') THEN performance.ppm END), 2) AS average_rating_90_days "
        "FROM performance JOIN operator ON performance.operator_id = operator.id "
        "GROUP BY operator.name "
        "ORDER BY average_rating_7_days DESC"
    ).fetchall()
    return render_template("rankings/index.html", rankings=rankings)
