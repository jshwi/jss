"""
app.routes.report
=================
"""
import json

from flask import Blueprint, Response, current_app, make_response, request

from app.extensions import csrf_protect

blueprint = Blueprint("report", __name__, url_prefix="/report")


@blueprint.route("/csp_violations", methods=["POST"])
@csrf_protect.exempt
def csp_report() -> Response:
    """Post Content Security Report to ``report-uri``.

    Log CSP violations JSON payload.

    :return: Response object with HTTP Status 204 (No Content) status.
    """
    current_app.logger.info(
        json.dumps(request.get_json(force=True), indent=4, sort_keys=True)
    )
    response = make_response()
    response.status_code = 204
    return response
