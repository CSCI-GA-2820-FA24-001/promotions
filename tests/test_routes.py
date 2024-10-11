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
TestPromotion API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from uuid import uuid4
from datetime import datetime, timezone
from wsgi import app
from service.common import status
from service.models import db, Promotion
from .factories import PromotionFactory
import uuid

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/promotions"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestPromotionResourceService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ############################################################
    # Utility function to bulk create promotions
    ############################################################
    def _create_promotions(self, count: int = 1) -> list:
        """Factory method to create promotions in bulk"""
        promotions = []
        for _ in range(count):
            test_promotion = PromotionFactory()
            response = self.client.post(BASE_URL, json=test_promotion.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test promotion",
            )
            new_promotion = response.get_json()
            test_promotion.id = new_promotion["id"]
            promotions.append(test_promotion)
        return promotions

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["service_name"], "Promotion Service")
        self.assertEqual(data["version"], "v1.0")
        self.assertEqual(data["endpoint"], "/promotions")

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------
    def test_get_promotion(self):
        """It should Get a single Promotion"""
        # get the id of a promotion
        test_promotion = self._create_promotions(1)[0]
        print("xxxxxx", f"{BASE_URL}/{test_promotion.id}")
        response = self.client.get(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_promotion.name)

    def test_get_promotion_not_found(self):
        """It should not Get a Promotion thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------
    def test_create_promotion(self):
        """It should Create a new Promotion"""
        test_promotion = PromotionFactory()
        logging.debug("Test Promotion: %s", test_promotion.serialize())
        response = self.client.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_promotion = response.get_json()
        self.assertEqual(new_promotion["name"], test_promotion.name)
        self.assertEqual(new_promotion["description"], test_promotion.description)
        self.assertEqual(
            datetime.fromisoformat(new_promotion["start_date"]).replace(
                tzinfo=timezone.utc
            ),
            test_promotion.start_date,
        )
        self.assertEqual(
            datetime.fromisoformat(new_promotion["end_date"]).replace(
                tzinfo=timezone.utc
            ),
            test_promotion.end_date,
        )
        self.assertEqual(new_promotion["active_status"], test_promotion.active_status)
        self.assertEqual(new_promotion["created_by"], test_promotion.created_by)
        self.assertEqual(new_promotion["updated_by"], test_promotion.updated_by)
        self.assertEqual(new_promotion["product_ids"], test_promotion.product_ids)
        self.assertEqual(
            new_promotion["extra"]["promotion_type"],
            test_promotion.extra["promotion_type"],
        )
        self.assertEqual(new_promotion["extra"]["value"], test_promotion.extra["value"])

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_promotion = response.get_json()
        self.assertEqual(new_promotion["name"], test_promotion.name)
        self.assertEqual(new_promotion["description"], test_promotion.description)
        self.assertEqual(
            datetime.fromisoformat(new_promotion["start_date"]).replace(
                tzinfo=timezone.utc
            ),
            test_promotion.start_date,
        )
        self.assertEqual(
            datetime.fromisoformat(new_promotion["end_date"]).replace(
                tzinfo=timezone.utc
            ),
            test_promotion.end_date,
        )
        self.assertEqual(new_promotion["active_status"], test_promotion.active_status)
        self.assertEqual(new_promotion["created_by"], test_promotion.created_by)
        self.assertEqual(new_promotion["updated_by"], test_promotion.updated_by)
        self.assertEqual(new_promotion["product_ids"], test_promotion.product_ids)
        self.assertEqual(
            new_promotion["extra"]["promotion_type"],
            test_promotion.extra["promotion_type"],
        )
        self.assertEqual(new_promotion["extra"]["value"], test_promotion.extra["value"])

    # ----------------------------------------------------------
    # TEST CREATE WITH 415 WRONG HEADERS
    # ----------------------------------------------------------
    def test_create_promotion_with_wrong_headers(self):
        """It should raise a 415 unsupported media type error"""
        test_promotion = PromotionFactory()
        logging.debug("Test Promotion: %s", test_promotion.serialize())
        response = self.client.post(
            BASE_URL,
            json=test_promotion.serialize(),
            headers={"Content-Type": "some wrong value"},
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    # ----------------------------------------------------------
    # TEST UPDATE
    # ----------------------------------------------------------
    def test_update_promotion(self):
        """It should update an existing promotion"""
        test_promotion = self._create_promotions(1)[0]

        updated_data = {
            "name": "Updated Promotion Name",
            "description": "Updated description",
            "start_date": test_promotion.start_date.isoformat(),
            "end_date": test_promotion.end_date.isoformat(),
            "active_status": not test_promotion.active_status,  # Flip the active status
            "created_by": test_promotion.created_by,
            "updated_by": str(uuid.uuid4()),
            "product_ids": test_promotion.product_ids,
            "extra": {"promotion_type": "percentage", "value": 15},
        }

        response = self.client.put(f"{BASE_URL}/{test_promotion.id}", json=updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_promotion = response.get_json()

        self.assertEqual(updated_promotion["name"], updated_data["name"])
        self.assertEqual(updated_promotion["description"], updated_data["description"])
        self.assertEqual(
            datetime.fromisoformat(updated_promotion["start_date"]).replace(
                tzinfo=timezone.utc
            ),
            test_promotion.start_date,
        )
        self.assertEqual(
            datetime.fromisoformat(updated_promotion["end_date"]).replace(
                tzinfo=timezone.utc
            ),
            test_promotion.end_date,
        )
        self.assertEqual(
            updated_promotion["active_status"], updated_data["active_status"]
        )
        self.assertEqual(updated_promotion["created_by"], updated_data["created_by"])
        self.assertEqual(updated_promotion["updated_by"], updated_data["updated_by"])
        self.assertEqual(updated_promotion["product_ids"], updated_data["product_ids"])
        self.assertEqual(
            updated_promotion["extra"]["promotion_type"],
            updated_data["extra"]["promotion_type"],
        )
        self.assertEqual(
            updated_promotion["extra"]["value"], updated_data["extra"]["value"]
        )

    # ----------------------------------------------------------
    # TEST UPDATE 400 BAD_REQUEST
    # ----------------------------------------------------------
    def test_update_promotion_bad_request(self):
        """It should not update an promotion with bad request"""
        test_promotion = self._create_promotions(1)[0]

        # bad update data structure
        updated_data = {
            "123": 123,
        }

        response = self.client.put(f"{BASE_URL}/{test_promotion.id}", json=updated_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------
    # TEST DELETE
    # ----------------------------------------------------------
    def test_delete_promotion(self):
        """It should Delete a Promotion"""
        test_promotion = self._create_promotions(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_non_existing_promotion(self):
        """It should Delete a Promotion even if it doesn't exist"""
        non_existent_id = uuid4()  # Generate a random UUID
        response = self.client.delete(f"{BASE_URL}/{non_existent_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    # ----------------------------------------------------------
    # TEST INVALID METHODS
    # ----------------------------------------------------------
    def test_delete_invalid_methods(self):
        """It should throw HTTP 405, METHOD_NOT_ALLOWED"""
        response = self.client.delete(f"{BASE_URL}")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
