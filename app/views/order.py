"""
app.views.order
===============
"""

import stripe
from flask import Blueprint, current_app, flash, redirect, request, url_for
from werkzeug import Response

from app.extensions import csrf_protect

blueprint = Blueprint("order", __name__, url_prefix="/order")


@blueprint.route("call", methods=["POST"])
@csrf_protect.exempt
def call() -> Response:
    """Book a call.

    :return: Response object.
    """
    session = stripe.checkout.Session
    price_data = session.CreateParamsLineItemPriceData(  # type: ignore
        product_data={"name": "Book a call"},
        unit_amount=int(current_app.config["PAYMENT_OPTIONS"]["price"]),
        currency="usd",
    )
    checkout_session = stripe.checkout.Session.create(
        api_key=current_app.config["STRIPE_SECRET_KEY"],
        line_items=[{"price_data": price_data, "quantity": 1}],  # type: ignore
        payment_method_types=["card"],
        mode="payment",
        success_url=f"{request.host_url}order/success",
        cancel_url=f"{request.host_url}order/cancel",
    )
    return redirect(checkout_session.url)  # type: ignore


@blueprint.route("success")
@csrf_protect.exempt
def success() -> Response:
    """Render template on success.

    :return: Success template.
    """
    flash("Thank you, your order has been placed.")
    return redirect(url_for("index"))


@blueprint.route("cancel")
@csrf_protect.exempt
def cancel() -> Response:
    """Render template on cancellation.

    :return: Response object redirecting user to index.
    """
    flash("Your order was canceled.")
    return redirect(url_for("index"))
