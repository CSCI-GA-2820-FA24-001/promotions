######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Promotion Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Promotion
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Promotion
from service.common import status  # HTTP Status Codes
from service.common.route_utils import check_content_type, parse_with_try


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")

######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# READ A PROMOTION
######################################################################
@app.route("/promotions/<uuid:promotion_id>", methods=["GET"])
def get_promotions(promotion_id):
    """
    Retrieve a single Promotion

    This endpoint will return a Promotion based on it's id
    """
    app.logger.info("Request to Retrieve a promotion with id [%s]", promotion_id)

    promotion = Promotion.find(promotion_id)

    if not promotion:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Promotion with id '{promotion_id}' was not found.",
        )

    app.logger.info("Returning promotion: %s", promotion.name)
    return jsonify(promotion.serialize()), status.HTTP_200_OK


######################################################################
# CREATE A NEW PROMOTION
######################################################################
@app.route("/promotions", methods=["POST"])
def create_promotions():
    """
    Create a Promotion
    This endpoint will create a Promotion based the data in the body that is posted
    """
    app.logger.info("Request to Create a Promotion...")
    check_content_type("application/json")

    promotion = Promotion()
    # Get the data from the request and deserialize it
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    promotion.deserialize(data)

    # Save the new Promotion to the database
    promotion.create()
    app.logger.info("Promotion with new id [%s] saved!", promotion.id)

    # Return the location of the new Promotion
    location_url = url_for("get_promotions", promotion_id=promotion.id, _external=True)
    return (
        jsonify(promotion.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# UPDATE PROMOTION
######################################################################
@app.route("/promotions/<uuid:promotion_id>", methods=["PUT"])
def update_promotion(promotion_id):
    """
    Update an existing Promotion

    This endpoint will update a Promotion based on the provided data
    """
    app.logger.info(f"Request to update promotion with id: {promotion_id}")
    promotion = Promotion.find(promotion_id)
    if not promotion:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Promotion with id '{promotion_id}' was not found.",
        )

    data = request.get_json()
    app.logger.info(f"Processing update with data: {data}")

    promotion.deserialize(data)

    promotion.update()
    app.logger.info(f"Promotion with ID [{promotion_id}] updated successfully.")

    return jsonify(promotion.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A PROMOTION
######################################################################
@app.route("/promotions/<uuid:promotion_id>", methods=["DELETE"])
def delete_promotions(promotion_id):
    """
    Delete a Promotion

    This endpoint will delete a Promotion based the id specified in the path
    """
    app.logger.info("Request to Delete a promotion with id [%s]", promotion_id)

    # Delete the Promotion if it exists
    promotion = Promotion.find(promotion_id)
    if promotion:
        app.logger.info("Promotion with ID: %d found.", promotion.id)
        promotion.delete()

    app.logger.info("Promotion with ID: %d delete complete.", promotion_id)
    return {}, status.HTTP_204_NO_CONTENT


######################################################################
# LIST ALL PROMOTIONS
######################################################################
@app.route("/promotions", methods=["GET"])
def list_promotions():
    """
    List all promotions

    This endpoint will list all promotions stored in the DB
    """
    app.logger.info("Request for a promotion list")

    promos = []

    # Parse any arguments from the query string
    name = request.args.get("name")
    product_id = request.args.get("product_id")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    start = parse_with_try(start_date)
    end = parse_with_try(end_date)
    exact_match = request.args.get("exact_match", "false").lower() in [
        "true",
        "yes",
        "1",
    ]
    active_status = request.args.get("active_status")
    created_by = request.args.get("created_by")
    updated_by = request.args.get("updated_by")

    if name:
        app.logger.info("Find by name: %s", name)
        promos = Promotion.find_by_name(name=name)
    elif product_id:
        app.logger.info("Find by product_id: %s", product_id)
        promos = Promotion.find_by_product_id(product_id=product_id)
    elif start and end:
        app.logger.info("Find by date range: %s --- %s", start_date, end_date)
        promos = Promotion.find_by_date_range(start_date=start, end_date=end)
    elif start:
        app.logger.info("Find by start_date: %s", start_date)
        promos = Promotion.find_by_start_date(start_date=start, exact_match=exact_match)
    elif end:
        app.logger.info("Find by end_date: %s", end_date)
        promos = Promotion.find_by_end_date(end_date=end, exact_match=exact_match)
    elif active_status:
        app.logger.info("Find by active_status: %s", active_status)
        active_status_value = active_status.lower() in ["true", "yes", "1"]
        promos = Promotion.find_by_active_status(active_status=active_status_value)
    elif created_by:
        app.logger.info("Find by creator: %s", created_by)
        promos = Promotion.find_by_creator(user_id=created_by)
    elif updated_by:
        app.logger.info("Find by updater: %s", updated_by)
        promos = Promotion.find_by_updater(user_id=updated_by)
    else:
        app.logger.info("Find all")
        promos = Promotion.query.all()

    result = [promotion.serialize() for promotion in promos]
    return jsonify(result), status.HTTP_200_OK


######################################################################
# ACTIVATE A PROMOTION
######################################################################


@app.route("/promotions/<promotion_id>/activate", methods=["PATCH"])
def activate_promotion(promotion_id):
    """Activate a promotion by setting its active_status to True"""
    promotion = Promotion.find(promotion_id)
    if not promotion:
        abort(404, f"Promotion with id {promotion_id} not found")
    promotion.active_status = True
    promotion.update()

    return (
        jsonify(message="Promotion activated", active_status=promotion.active_status),
        200,
    )


@app.route("/promotions/<promotion_id>/deactivate", methods=["PATCH"])
def deactivate_promotion(promotion_id):
    """Deactivate a promotion by setting its active_status to False"""
    promotion = Promotion.find(promotion_id)
    if not promotion:
        abort(404, f"Promotion with id {promotion_id} not found")
    promotion.active_status = False
    promotion.update()
    return (
        jsonify(message="Promotion deactivated", active_status=promotion.active_status),
        200,
    )
