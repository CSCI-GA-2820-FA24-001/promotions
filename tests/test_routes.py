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
from unittest.mock import patch

from uuid import uuid4
from datetime import datetime, timezone
from urllib.parse import quote_plus
from werkzeug.exceptions import InternalServerError
from wsgi import app
from service.common import status
from service.models import db, Promotion
from .factories import PromotionFactory

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
    def _create_promotions(self, count: int = 1) -> list[Promotion]:
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
        """It should serve the home page HTML"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(b"<title>Promotion Demo RESTful Service</title>", resp.data)


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

    def test_create_promotion_no_content_type(self):
        """It should raise a 415 unsupported media type error"""
        response = self.client.post(BASE_URL)
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
            "updated_by": str(uuid4()),
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

    def test_update_promotion_with_non_uuid_id(self):
        """It should raise a 404 Method Not Found error when a non-UUID type promotion ID is used"""

        non_uuid_id = "not-a-uuid"

        response = self.client.put(f"{BASE_URL}/{non_uuid_id}", json={})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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
    # TEST UPDATE 404 NOT_FOUND
    # ----------------------------------------------------------
    def test_update_promotion_not_found(self):
        """It should not update a non-existing promotion"""
        non_existent_id = uuid4()
        updated_data = {
            "name": "Updated Promotion Name",
            "description": "Updated description",
            "start_date": datetime.now(timezone.utc).isoformat(),
            "end_date": datetime.now(timezone.utc).isoformat(),
            "active_status": True,
            "created_by": str(uuid4()),
            "updated_by": str(uuid4()),
            "product_ids": [str(uuid4())],
            "extra": {"promotion_type": "percentage", "value": 15},
        }

        response = self.client.put(f"{BASE_URL}/{non_existent_id}", json=updated_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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

    # ----------------------------------------------------------
    # TEST LIST
    # ----------------------------------------------------------
    def test_list_promotions(self):
        """It should list all promotions"""
        test_list_promos = self._create_promotions(2)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertEqual(
            len(data), len(test_list_promos)
        )  # check first if number of promos equal the number stored in the DB

        for i, promo in enumerate(test_list_promos):
            self.assertEqual(data[i]["name"], promo.name)
            self.assertEqual(data[i]["description"], promo.description)
            self.assertEqual(
                datetime.fromisoformat(data[i]["start_date"]).replace(
                    tzinfo=timezone.utc
                ),
                promo.start_date,
            )
            self.assertEqual(
                datetime.fromisoformat(data[i]["end_date"]).replace(
                    tzinfo=timezone.utc
                ),
                promo.end_date,
            )
            self.assertEqual(data[i]["active_status"], promo.active_status)
            self.assertEqual(data[i]["created_by"], promo.created_by)
            self.assertEqual(data[i]["updated_by"], promo.updated_by)
            self.assertEqual(data[i]["product_ids"], promo.product_ids)
            self.assertEqual(
                data[i]["extra"]["promotion_type"], promo.extra["promotion_type"]
            )
            self.assertEqual(data[i]["extra"]["value"], promo.extra["value"])

    # ----------------------------------------------------------
    # TEST QUERY
    # ----------------------------------------------------------
    def test_query_by_name(self):
        """It should Query Promotions by name"""
        promotions = self._create_promotions(5)
        test_name = promotions[0].name
        name_count = len(
            [promotion for promotion in promotions if promotion.name == test_name]
        )
        response = self.client.get(
            BASE_URL, query_string=f"name={quote_plus(test_name)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), name_count)
        # check the data just to be sure
        for promotion in data:
            self.assertEqual(promotion["name"], test_name)

    def test_query_by_product_id(self):
        """It should query by Product id"""
        promotions = self._create_promotions(10)
        test_product_id = promotions[0].product_ids[0]
        product_id_count = len(
            [
                promotion
                for promotion in promotions
                if test_product_id in promotion.product_ids
            ]
        )
        response = self.client.get(
            BASE_URL, query_string=f"product_id={quote_plus(test_product_id)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), product_id_count)
        # check the data just to be sure
        for promotion in data:
            self.assertTrue(test_product_id in promotion["product_ids"])

    def test_query_by_date_range(self):
        """It should query by date range"""
        promotions = self._create_promotions(10)
        test_start_date = promotions[0].start_date
        test_end_date = promotions[0].end_date
        date_range_count = len(
            [
                promotion
                for promotion in promotions
                if promotion.start_date <= test_end_date
                and promotion.end_date >= test_start_date
            ]
        )
        response = self.client.get(
            BASE_URL,
            query_string=f"start_date={quote_plus(test_start_date.isoformat())}"
            + f"&end_date={quote_plus(test_end_date.isoformat())}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), date_range_count)
        # check the data just to be sure
        for promotion in data:
            self.assertTrue(
                datetime.fromisoformat(promotion["start_date"]).replace(
                    tzinfo=timezone.utc
                )
                <= test_end_date
                and datetime.fromisoformat(promotion["end_date"]).replace(
                    tzinfo=timezone.utc
                )
                >= test_start_date
            )

    def test_query_by_start_date(self):
        """It should query by start date"""
        promotions = self._create_promotions(10)
        test_start_date = promotions[0].start_date
        start_date_count = len(
            [
                promotion
                for promotion in promotions
                if promotion.start_date >= test_start_date
            ]
        )
        response = self.client.get(
            BASE_URL,
            query_string=f"start_date={quote_plus(test_start_date.isoformat())}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), start_date_count)
        # check the data just to be sure
        for promotion in data:
            self.assertTrue(
                datetime.fromisoformat(promotion["start_date"]).replace(
                    tzinfo=timezone.utc
                )
                >= test_start_date
            )

    def test_query_by_start_date_exact_match(self):
        """It should query by start date (exact match)"""
        promotions = self._create_promotions(10)
        test_start_date = promotions[0].start_date
        start_date_count = len(
            [
                promotion
                for promotion in promotions
                if promotion.start_date == test_start_date
            ]
        )
        response = self.client.get(
            BASE_URL,
            query_string=f"start_date={quote_plus(test_start_date.isoformat())}&exact_match=true",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), start_date_count)
        # check the data just to be sure
        for promotion in data:
            self.assertTrue(
                datetime.fromisoformat(promotion["start_date"]).replace(
                    tzinfo=timezone.utc
                )
                == test_start_date
            )

    def test_query_by_end_date(self):
        """It should query by end date"""
        promotions = self._create_promotions(10)
        test_end_date = promotions[0].end_date
        end_date_count = len(
            [
                promotion
                for promotion in promotions
                if promotion.end_date <= test_end_date
            ]
        )
        response = self.client.get(
            BASE_URL,
            query_string=f"end_date={quote_plus(test_end_date.isoformat())}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), end_date_count)
        # check the data just to be sure
        for promotion in data:
            self.assertTrue(
                datetime.fromisoformat(promotion["end_date"]).replace(
                    tzinfo=timezone.utc
                )
                <= test_end_date
            )

    def test_query_by_end_date_exact_match(self):
        """It should query by end date (exact match)"""
        promotions = self._create_promotions(10)
        test_end_date = promotions[0].end_date
        end_date_count = len(
            [
                promotion
                for promotion in promotions
                if promotion.end_date == test_end_date
            ]
        )
        response = self.client.get(
            BASE_URL,
            query_string=f"end_date={quote_plus(test_end_date.isoformat())}&exact_match=true",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), end_date_count)
        # check the data just to be sure
        for promotion in data:
            self.assertTrue(
                datetime.fromisoformat(promotion["end_date"]).replace(
                    tzinfo=timezone.utc
                )
                == test_end_date
            )

    def test_query_by_active_status(self):
        """It should query by active status"""
        promotions = self._create_promotions(5)
        test_active_status = promotions[0].active_status
        active_status_count = len(
            [
                promotion
                for promotion in promotions
                if promotion.active_status == test_active_status
            ]
        )
        response = self.client.get(
            BASE_URL,
            query_string=f"active_status={quote_plus(str(test_active_status))}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), active_status_count)
        # check the data just to be sure
        for promotion in data:
            self.assertEqual(promotion["active_status"], test_active_status)

    def test_query_by_creator(self):
        """It should query by creator"""
        promotions = self._create_promotions(5)
        test_created_by = promotions[0].created_by
        creator_count = len(
            [
                promotion
                for promotion in promotions
                if promotion.created_by == test_created_by
            ]
        )
        response = self.client.get(
            BASE_URL,
            query_string=f"created_by={quote_plus(test_created_by)}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), creator_count)
        # check the data just to be sure
        for promotion in data:
            self.assertEqual(promotion["created_by"], test_created_by)

    def test_query_by_updater(self):
        """It should query by updater"""
        promotions = self._create_promotions(5)
        test_updated_by = promotions[0].updated_by
        updater_count = len(
            [
                promotion
                for promotion in promotions
                if promotion.updated_by == test_updated_by
            ]
        )
        response = self.client.get(
            BASE_URL,
            query_string=f"updated_by={quote_plus(test_updated_by)}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), updater_count)
        # check the data just to be sure
        for promotion in data:
            self.assertEqual(promotion["updated_by"], test_updated_by)

    # ----------------------------------------------------------
    # TEST LIST (Sad Path)
    # ----------------------------------------------------------
    def test_list_promotions_empty(self):
        """It should return an empty list if no promotions exist"""
        response = self.client.get(BASE_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_activate_promotion(self):
        """It should activate a promotion"""
        test_promotion = self._create_promotions(1)[0]
        test_promotion.active_status = False
        response = self.client.patch(f"{BASE_URL}/{test_promotion.id}/activate")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertTrue(data["active_status"])
        self.assertEqual(data["message"], "Promotion activated")

    def test_deactivate_promotion(self):
        """It should deactivate a promotion"""
        test_promotion = self._create_promotions(1)[0]
        test_promotion.active_status = True
        response = self.client.patch(f"{BASE_URL}/{test_promotion.id}/deactivate")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertFalse(data["active_status"])
        self.assertEqual(data["message"], "Promotion deactivated")

    def test_activate_promotion_not_found(self):
        """It should return 404 if the promotion to activate does not exist"""
        sample_uuid = str(uuid4())
        response = self.client.patch(f"{BASE_URL}/{sample_uuid}/activate")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_deactivate_promotion_not_found(self):
        """It should return 404 if the promotion to deactivate does not exist"""
        sample_uuid = str(uuid4())
        response = self.client.patch(f"{BASE_URL}/{sample_uuid}/deactivate")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------
    # TEST LIST Query By Attributes (Sad Path)
    # ----------------------------------------------------------
    def test_query_by_name_empty(self):
        """It should Query Promotions by name (empty)"""
        response = self.client.get(BASE_URL, query_string="name=hello")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_query_by_product_id_empty(self):
        """It should Query Promotions by product_id (empty)"""
        response = self.client.get(BASE_URL, query_string="product_id=hello")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_query_by_start_date_empty(self):
        """It should Query Promotions by start date (empty)"""
        response = self.client.get(BASE_URL, query_string="start_date=2023-12-31")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_query_by_start_date_wrong_date_format(self):
        """It should Query Promotions by start date (empty + wrong date format)"""
        response = self.client.get(
            BASE_URL, query_string=f"start_date={quote_plus('Wrong Date')}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_query_by_end_date_wrong_date_format(self):
        """It should Query Promotions by end date (empty + wrong date format)"""
        response = self.client.get(
            BASE_URL, query_string=f"end_date={quote_plus('Wrong Date')}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_query_by_date_range_wrong_date_format(self):
        """It should Query Promotions by date range (empty + wrong date format)"""
        response = self.client.get(
            BASE_URL,
            query_string=f"start_date={quote_plus('Wrong Date')}&end_date={quote_plus('Wrong Date')}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    # ----------------------------------------------------------
    # TEST INTERNAL SERVER ERROR 500
    # ----------------------------------------------------------
    @patch("service.routes.Promotion.find_by_name")
    def test_internal_server_error(self, internal_error_mock):
        """It should raise internal server error"""
        # use Internal Server Error to mock abort 500 status code
        internal_error_mock.side_effect = InternalServerError(
            "An internal server error occurred"
        )

        response = self.client.get(BASE_URL, query_string="name=hello")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
