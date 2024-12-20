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
# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa

"""
Promotions Steps
Steps file for Promotions.feature
For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from compare3 import expect
from behave import given  # pylint: disable=no-name-in-module

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

WAIT_TIMEOUT = 60

PROMOTIONS_API_ENDPOINT = "api/promotions"


@given("the following promotions")
def step_impl(context):
    """Delete all promotions and load new ones"""

    # Get a list all of the promotions
    rest_endpoint = f"{context.base_url}/{PROMOTIONS_API_ENDPOINT}"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)
    # and delete them one by one
    for promotion in context.resp.json():
        context.resp = requests.delete(
            f"{rest_endpoint}/{promotion['id']}", timeout=WAIT_TIMEOUT
        )
        expect(context.resp.status_code).equal_to(HTTP_204_NO_CONTENT)

    # load the database with new promotions
    for row in context.table:
        print(row)
        payload = {
            "id": row["id"],
            "name": row["name"],
            "start_date": row["start_date"],
            "end_date": row["end_date"],
            "active_status": row["active_status"].lower() == "true",
            "created_by": row["created_by"],
            "updated_by": row["updated_by"],
            # Optional fields
            "description": row.get("description"),
            "product_ids": row.get("product_ids"),
            "extra": row.get("extra"),
        }

        # Create a new promotion
        create_resp = requests.post(rest_endpoint, json=payload, timeout=WAIT_TIMEOUT)
        expect(create_resp.status_code).equal_to(HTTP_201_CREATED)
        context.last_created_uuid = create_resp.json()["id"]
