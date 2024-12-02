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

from functools import wraps
from flask import abort, request
from flask import current_app as app  # Import Flask application
from flask_restx import Api, Resource, fields, reqparse, inputs
from service.models import Promotion
from service.common import status  # HTTP Status Codes
from service.common.route_utils import parse_with_try

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(
    app,
    version="1.0.0",
    title="Promotion Demo REST API Service",
    description="This is a sample server Promotion store server.",
    default="promotions",
    default_label="Promotion operations",
    doc="/apidocs",
    prefix="/api",
)


######################################################################
# API Model Definition
######################################################################
# Define the API model for Promotion Creation
create_model = api.model(
    "Promotion",
    {
        "product_ids": fields.Raw(
            description="A list of product IDs associated with the promotion, stored as a JSON array.",
            example=["product_id_1", "product_id_2"],
            required=False,
        ),
        "name": fields.String(
            required=True,
            description="The name of the promotion.",
            example="Summer Sale",
        ),
        "description": fields.String(
            description="A detailed description of the promotion.",
            example="Get up to 50% off on summer clothing items.",
        ),
        "start_date": fields.DateTime(
            required=True,
            description="The start date and time of the promotion.",
            dt_format="iso8601",
        ),
        "end_date": fields.DateTime(
            required=True,
            description="The end date and time of the promotion.",
            dt_format="iso8601",
        ),
        "active_status": fields.Boolean(
            required=True,
            description="A boolean indicating whether the promotion is active.",
        ),
        "created_by": fields.String(
            required=True, description="The UUID of the user who created the promotion."
        ),
        "updated_by": fields.String(
            required=True,
            description="The UUID of the user who last updated the promotion.",
        ),
        "extra": fields.Raw(
            description="Additional metadata for the promotion, stored as a JSON object.",
            required=False,
            example={"key": "value"},
        ),
    },
)

# Define the API model for Promotion
promotion_model = api.inherit(
    "PromotionModel",
    create_model,
    {
        "id": fields.String(
            description="A unique identifier for the promotion, generated automatically as a UUID.",
            readOnly=True,
        ),
        "created_at": fields.DateTime(
            readOnly=True,
            description="The timestamp when the promotion was created.",
            dt_format="iso8601",
        ),
        "updated_at": fields.DateTime(
            readOnly=True,
            description="The timestamp when the promotion was last updated.",
            dt_format="iso8601",
        ),
    },
)


######################################################################
# Setup the request parser for promotions
######################################################################
args_config = [
    ("start_date", str, "args", False, "Filter promotions starting from this date"),
    ("end_date", str, "args", False, "Filter promotions ending by this date"),
    (
        "exact_match_start_date",
        inputs.boolean,
        "args",
        False,
        "Apply exact matching for start date",
    ),
    (
        "exact_match_end_date",
        inputs.boolean,
        "args",
        False,
        "Apply exact matching for end date",
    ),
    ("name", str, "args", False, "Filter promotions by name"),
    ("product_id", str, "args", False, "Filter promotions by product ID"),
    (
        "active_status",
        inputs.boolean,
        "args",
        False,
        "Filter promotions by active status",
    ),
    ("created_by", str, "args", False, "Filter promotions by creator user ID"),
    ("updated_by", str, "args", False, "Filter promotions by updater user ID"),
]


# Init promotion args
promotion_args = reqparse.RequestParser()

for arg_name, arg_type, location, required, help_text in args_config:
    promotion_args.add_argument(
        arg_name, type=arg_type, location=location, required=required, help=help_text
    )


######################################################################
# Content Type Check Decorator
######################################################################
def require_content_type(content_type):
    """Decorator to require a specific content type for this endpoint"""

    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            # Check if the Content-Type header matches the expected content type
            if request.headers.get("Content-Type", "") != content_type:
                app.logger.error(
                    "Invalid Content-Type: %s",
                    request.headers.get("Content-Type", "Content-Type not set"),
                )
                # If not, abort the request and return an error message
                abort(
                    status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    f"Content-Type must be {content_type}",
                )
            return func(*args, **kwargs)

        return decorated_function

    return decorator


######################################################################
# Health Endpoint
######################################################################
@app.route("/health")
def health():
    """Health Status"""
    return {"status": "OK"}, status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
# FLASK-RESTX APIs
######################################################################


@api.route("/promotions/<uuid:promotion_id>")
@api.param("promotion_id", "The Promotion identifier")
@api.response(404, "Promotion not found")
class PromotionResource(Resource):
    """
    PromotionResource class

    Allows the manipulation of a single Promotion
    GET /promotion{id} - Returns a Promotion with the id
    PUT /promotion{id} - Update a Promotion with the id
    DELETE /promotion{id} -  Deletes a Promotion with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A PROMOTION
    # ------------------------------------------------------------------
    @api.doc("get_promotion")
    @api.response(404, "Promotion not found")
    @api.marshal_with(promotion_model)
    def get(self, promotion_id):
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
        return promotion.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING PROMOTION
    # ------------------------------------------------------------------
    @api.doc("update_promotion")
    @api.response(404, "Promotion not found")
    @api.response(400, "The posted Promotion data was not valid")
    @api.expect(promotion_model)
    @api.marshal_with(promotion_model)
    def put(self, promotion_id):
        """
        Update a Promotion

        This endpoint will update a Promotion based the body that is posted
        """
        app.logger.info("Request to Update a promotion with id [%s]", promotion_id)
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Promotion with id '{promotion_id}' was not found.",
            )
        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        promotion.deserialize(data)
        promotion.id = promotion_id
        promotion.update()
        return promotion.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A PROMOTION
    # ------------------------------------------------------------------
    @api.doc("delete_promotion")
    @api.response(204, "Promotion deleted")
    def delete(self, promotion_id):
        """
        Delete a Promotion

        This endpoint will delete a Promotion based the id specified in the path
        """
        app.logger.info("Request to Delete a promotion with id [%s]", promotion_id)
        promotion = Promotion.find(promotion_id)
        if promotion:
            promotion.delete()
            app.logger.info("Promotion with id [%s] was deleted", promotion_id)
            return "", status.HTTP_204_NO_CONTENT
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Promotion with id '{promotion_id}' was not found.",
        )


######################################################################
#  PATH: /promotions
######################################################################
@api.route("/promotions", strict_slashes=False)
class PromotionCollection(Resource):
    """Handles all interactions with collections of Promotions"""

    # ------------------------------------------------------------------
    # LIST ALL PROMOTIONS
    # ------------------------------------------------------------------
    @api.doc("list_promotions")
    @api.expect(promotion_args, validate=True)
    @api.marshal_list_with(promotion_model)
    def get(self):
        """Returns all of the Promotions"""
        app.logger.info("Request to list promotions...")
        promotions = []
        args = promotion_args.parse_args()

        query = Promotion.query

        # Handle Date filtering
        start_date = parse_with_try(args.get("start_date"))
        end_date = parse_with_try(args.get("end_date"))

        if start_date and end_date:
            query = Promotion.find_by_date_range(query, start_date, end_date)
        elif start_date:
            exact_match = args.get("exact_match_start_date", False)
            query = Promotion.find_by_start_date(
                query, start_date, exact_match=exact_match
            )
        elif end_date:
            exact_match = args.get("exact_match_end_date", False)
            query = Promotion.find_by_end_date(query, end_date, exact_match=exact_match)

        # Other filtering
        filter_handlers = {
            "name": lambda val: Promotion.find_by_name(query, val),
            "product_id": lambda val: Promotion.find_by_product_id(query, val),
            "active_status": lambda val: Promotion.find_by_active_status(query, val),
            "created_by": lambda val: Promotion.find_by_creator(query, user_id=val),
            "updated_by": lambda val: Promotion.find_by_updater(query, user_id=val),
        }

        for key, handler in filter_handlers.items():
            value = args.get(key)  # This will use None if the key isn't present
            if value is not None:
                app.logger.info(f"Applying filter by {key}: {value}")
                query = handler(value)

        promotions = query.all()
        results = [promotion.serialize() for promotion in promotions]
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW PROMOTION
    # ------------------------------------------------------------------
    @api.doc(
        "create_promotions",
        consumes="application/json",
        responses={415: "Unsupported Media Type"},
    )
    @api.response(400, "The posted data was not valid")
    @api.expect(create_model)
    @api.marshal_with(promotion_model, code=201)
    @require_content_type("application/json")
    def post(self):
        """
        Create a Promotion
        This endpoint will create a Promotion based the data in the body that is posted
        """
        app.logger.info("Request to Create a Promotion")
        promotion = Promotion()
        app.logger.debug("Payload = %s", api.payload)
        promotion.deserialize(api.payload)
        promotion.create()
        app.logger.info("Promotion with new id [%s] created!", promotion.id)
        location_url = api.url_for(
            PromotionResource, promotion_id=promotion.id, _external=True
        )

        return (
            promotion.serialize(),
            status.HTTP_201_CREATED,
            {"Location": location_url},
        )


######################################################################
#  PATH: /promotions/{id}/activate
######################################################################
@api.route("/promotions/<promotion_id>/activate")
@api.param("promotion_id", "The Promotion identifier")
class ActivateResource(Resource):
    """Activate actions on a Promotion"""

    @api.doc("activate_promotions")
    @api.response(404, "Promotion not found")
    @api.response(200, "Promotion activated")
    def patch(self, promotion_id):
        """
        Activate a Promotion

        This endpoint will activate a Promotion and make it active
        """
        app.logger.info("Request to activate a Promotion")
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(
                status.HTTP_404_NOT_FOUND, f"Promotion with id {promotion_id} not found"
            )
        promotion.active_status = True
        promotion.update()
        app.logger.info("promotion with id [%s] has been activated!", promotion.id)
        return (
            {
                "message": "Promotion activated",
                "active_status": promotion.active_status,
            },
            status.HTTP_200_OK,
        )


######################################################################
#  PATH: /promotions/{id}/deactivate
######################################################################
@api.route("/promotions/<promotion_id>/deactivate")
@api.param("promotion_id", "The Promotion identifier")
class DeactivateResource(Resource):
    """deactivate actions on a Promotion"""

    @api.doc("deactivate_promotions")
    @api.response(404, "Promotion not found")
    @api.response(200, "Promotion deactivated")
    def patch(self, promotion_id):
        """
        Deactivate a Promotion

        This endpoint will deactivate a Promotion and make it non-active
        """
        app.logger.info("Request to deactivate a Promotion")
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(
                status.HTTP_404_NOT_FOUND, f"Promotion with id {promotion_id} not found"
            )
        promotion.active_status = False
        promotion.update()
        app.logger.info("promotion with id [%s] has been deactivated!", promotion.id)

        return (
            {
                "message": "Promotion deactivated",
                "active_status": promotion.active_status,
            },
            status.HTTP_200_OK,
        )
