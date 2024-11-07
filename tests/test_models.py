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
Test cases for Pet Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from unittest.mock import patch
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from wsgi import app
from service.models import Promotion, DataValidationError, db
from .factories import PromotionFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

# Predefined constant values for test data to ensure consistency and readability
NAME = "Holiday Sale"
START_DATE = "2023-12-01T00:00:00"
END_DATE = "2023-12-31T23:59:59"
ACTIVE_STATUS = True
CREATED_BY = "d8e8fca2-dc0f-4c68-8f73-dcd8fca9e6d3"
UPDATED_BY = "d8e8fca2-dc0f-4c68-8f73-dcd8fca9e6d3"
PRODUCT_IDS = ["a4d8fca2-dc0f-4c68-8f73-dcd8fca9e6d3"]
DESCRIPTION = "Biggest holiday sale!"
EXTRA = {"promotion_type": "discount", "value": 10}


######################################################################
#  P R O M O T I O N   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestPromotion(TestCase):
    """Test Cases for Promotion Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_promotion_success(self):
        """It should create a Promotion"""

        expected_active_status = True
        expected_extra = {
            "promotion_type": "description",
            "value": None,
        }

        promotion = PromotionFactory(
            active_status=expected_active_status, extra=expected_extra
        )

        promotion.create()

        self.assertIsNotNone(
            promotion.id, "The promotion should have an ID after creation"
        )

        found = Promotion.all()
        self.assertEqual(
            len(found), 1, "There should be exactly one promotion in the database"
        )

        data = Promotion.find(promotion.id)
        self.assertIsNotNone(data, "The promotion should be found by ID")

        # Verify that all fields were correctly set
        self.assertEqual(data.name, promotion.name)
        self.assertEqual(data.description, promotion.description)
        self.assertEqual(data.start_date, promotion.start_date)
        self.assertEqual(data.end_date, promotion.end_date)
        self.assertEqual(data.active_status, expected_active_status)
        self.assertEqual(data.created_by, promotion.created_by)
        self.assertEqual(data.updated_by, promotion.updated_by)
        self.assertEqual(data.created_at, promotion.created_at)
        self.assertEqual(data.updated_at, promotion.updated_at)
        self.assertEqual(data.product_ids, promotion.product_ids)
        self.assertEqual(data.extra["promotion_type"], expected_extra["promotion_type"])
        self.assertEqual(data.extra["value"], expected_extra["value"])

    def test_create_a_promotion_with_invalid_data(self):
        """It should raise an exception when creating a promotion with invalid data"""

        promotion = PromotionFactory(name=None)

        with self.assertRaises(DataValidationError):
            promotion.create()

    def test_update_a_promotion_success(self):
        """It should successfully update a promotion"""
        promotion = PromotionFactory()
        promotion.create()

        new_name = "Updated Promotion Name"
        promotion.name = new_name
        promotion.update()

        updated_promotion = Promotion.find(promotion.id)

        self.assertEqual(updated_promotion.name, new_name)

    def test_update_promotion_with_invalid_data(self):
        """It should raise an exception if the update fails"""

        promotion = PromotionFactory()
        promotion.create()

        promotion.name = None

        with self.assertRaises(DataValidationError):
            promotion.update()

    def test_delete_a_promotion_success(self):
        """It should successfully delete a promotion"""
        promotion = PromotionFactory()
        promotion.create()
        created_promotion = Promotion.find(promotion.id)
        self.assertIsNotNone(created_promotion)

        promotion.delete()

        deleted_promotion = Promotion.find(promotion.id)
        self.assertIsNone(
            deleted_promotion, "The promotion should be deleted from the database"
        )

    @patch("service.models.db.session.delete")  # Mocking the session.delete method
    def test_delete_a_promotion_raises_exception(self, mock_delete):
        """It should raise an exception if deleting the promotion fails"""

        promotion = PromotionFactory()
        promotion.create()

        mock_delete.side_effect = Exception("Database delete failed")

        with self.assertRaises(DataValidationError) as context:
            promotion.delete()

        # Check that the error message is as expected
        self.assertTrue("Database delete failed" in str(context.exception))

    def test_promotion_deserialize_success(self):
        """It should successfully deserialize a valid dictionary into a Promotion"""

        data = {
            "name": NAME,
            "start_date": START_DATE,
            "end_date": END_DATE,
            "active_status": ACTIVE_STATUS,
            "created_by": CREATED_BY,
            "updated_by": UPDATED_BY,
        }

        # Create a Promotion instance and deserialize the data
        promotion = PromotionFactory()
        promotion.deserialize(data)

        # Assertions using constants
        self.assertEqual(promotion.name, NAME)
        self.assertEqual(promotion.start_date, datetime.fromisoformat(START_DATE))
        self.assertEqual(promotion.end_date, datetime.fromisoformat(END_DATE))
        self.assertTrue(promotion.active_status)
        self.assertEqual(promotion.created_by, UUID(CREATED_BY))
        self.assertEqual(promotion.updated_by, UUID(UPDATED_BY))

    def test_promotion_deserialize_missing_required_fields(self):
        """It should raise a DataValidationError when required fields are missing"""

        # Missing the 'name' field
        data = {
            "start_date": START_DATE,
            "end_date": END_DATE,
            "active_status": ACTIVE_STATUS,
            "created_by": CREATED_BY,
            "updated_by": UPDATED_BY,
        }

        promotion = PromotionFactory()

        # Assert that deserialization raises a DataValidationError for missing required fields
        with self.assertRaises(DataValidationError) as context:
            promotion.deserialize(data)

        self.assertTrue("Invalid Promotion: missing name" in str(context.exception))

    def test_promotion_deserialize_type_error(self):
        """It should raise a DataValidationError when any field has an incorrect type"""

        data = {
            "name": NAME,
            "start_date": 12345,  # Invalid type
            "end_date": END_DATE,
            "active_status": ACTIVE_STATUS,
            "created_by": CREATED_BY,
            "updated_by": UPDATED_BY,
        }

        promotion = PromotionFactory()

        with self.assertRaises(DataValidationError) as context:
            promotion.deserialize(data)

        self.assertTrue(
            "Invalid Promotion: body of request contained bad or no data"
            in str(context.exception)
        )

    def test_find_by_name_success(self):
        """It should return promotions with the specified name"""

        promotion1 = PromotionFactory(name="Black Friday Sale")
        promotion2 = PromotionFactory(name="Holiday Sale")
        promotion1.create()
        promotion2.create()

        found_promotions = Promotion.find_by_name("Holiday Sale")
        self.assertEqual(found_promotions.count(), 1)
        self.assertEqual(found_promotions.first().name, "Holiday Sale")

    def test_find_by_name_not_found(self):
        """It should return an empty result when no promotions with the given name are found"""

        found_promotions = Promotion.find_by_name("Non-existent Sale")
        self.assertEqual(found_promotions.count(), 0)

    def test_find_by_product_id_success(self):
        """It should return promotions containing a specified product ID"""
        product_id = "prod123"
        promotion1 = PromotionFactory(product_ids=[product_id])
        promotion2 = PromotionFactory(product_ids=["prod456"])  # Different product ID
        promotion1.create()
        promotion2.create()

        found_promotions = Promotion.find_by_product_id(product_id)
        self.assertEqual(len(found_promotions), 1)
        self.assertIn(product_id, found_promotions[0].product_ids)

    def test_find_by_product_id_not_found(self):
        """It should return an empty list when no promotions contain the given product ID"""
        found_promotions = Promotion.find_by_product_id("nonexistent123")
        self.assertEqual(len(found_promotions), 0)

    def test_find_by_start_date_exact_match(self):
        """It should find promotions that start exactly on a specified date when exact_match is True."""
        exact_start_date = datetime(2023, 12, 1)
        promotion = PromotionFactory(start_date=exact_start_date)
        promotion.create()

        found_promotions = Promotion.find_by_start_date(
            exact_start_date, exact_match=True
        )
        self.assertEqual(len(found_promotions), 1)
        self.assertEqual(found_promotions[0].start_date, exact_start_date)

    def test_find_by_start_date_on_or_after(self):
        """It should find promotions that start on or after a specified date when exact_match is False."""
        start_date = datetime(2023, 12, 1)
        promotion1 = PromotionFactory(start_date=start_date)
        promotion2 = PromotionFactory(
            start_date=start_date + timedelta(days=10)
        )  # Starts 10 days later
        promotion1.create()
        promotion2.create()

        found_promotions = Promotion.find_by_start_date(start_date, exact_match=False)
        self.assertEqual(len(found_promotions), 2)

        promotion_dates = {promo.start_date for promo in found_promotions}
        self.assertIn(start_date, promotion_dates)
        self.assertIn(start_date + timedelta(days=10), promotion_dates)

    def test_find_by_start_date_no_exact_matches(self):
        """It should return an empty list if no promotions start exactly on the given date when exact_match is True."""
        start_date = datetime(2023, 12, 1)
        promotion = PromotionFactory(start_date=start_date + timedelta(days=1))
        promotion.create()

        found_promotions = Promotion.find_by_start_date(start_date, exact_match=True)
        self.assertEqual(len(found_promotions), 0)

    def test_find_by_start_date_no_matches_on_or_after(self):
        """It should return an empty list if no promotions start on or after the given date when exact_match is False."""
        start_date = datetime(2023, 12, 1)
        promotion = PromotionFactory(start_date=start_date - timedelta(days=1))
        promotion.create()

        found_promotions = Promotion.find_by_start_date(start_date, exact_match=False)
        self.assertEqual(len(found_promotions), 0)

    def test_find_by_end_date_exact_match(self):
        """It should find promotions that end exactly on a specified date when exact_match is True."""
        exact_end_date = datetime(2023, 12, 31)
        PromotionFactory(
            end_date=exact_end_date,
        ).create()
        PromotionFactory(
            end_date=datetime(2024, 1, 10),
        ).create()

        found_promotions = Promotion.find_by_end_date(exact_end_date, exact_match=True)
        self.assertEqual(len(found_promotions), 1)

    def test_find_by_end_date_on_or_before(self):
        """It should find promotions that end on or before a specified date when exact_match is False."""
        target_date = datetime(2024, 1, 5)
        PromotionFactory(
            name="End of Year Sale",
            start_date=datetime(2023, 11, 20),
            end_date=datetime(2023, 12, 31),
        ).create()
        PromotionFactory(
            name="New Year Sale",
            start_date=datetime(2023, 12, 25),
            end_date=target_date,
        ).create()

        found_promotions = Promotion.find_by_end_date(target_date, exact_match=False)
        self.assertEqual(len(found_promotions), 2)
        promotion_names = {promo.name for promo in found_promotions}
        self.assertTrue("End of Year Sale" in promotion_names)
        self.assertTrue("New Year Sale" in promotion_names)

    def test_find_by_end_date_no_exact_matches(self):
        """It should return an empty list if no promotions end exactly on the given date when exact_match is True."""
        PromotionFactory(
            end_date=datetime(2024, 1, 15),
        ).create()

        non_existent_end_date = datetime(2024, 1, 14)
        found_promotions = Promotion.find_by_end_date(
            non_existent_end_date, exact_match=True
        )
        self.assertEqual(len(found_promotions), 0)

    def test_find_by_end_date_no_matches_on_or_before(self):
        """It should return an empty list if no promotions end on or before the given early date when exact_match is False."""
        PromotionFactory(
            end_date=datetime(2024, 2, 28),
        ).create()

        early_date = datetime(2024, 1, 15)
        found_promotions = Promotion.find_by_end_date(early_date, exact_match=False)
        self.assertEqual(len(found_promotions), 0)

    def test_find_by_date_range_success(self):
        """It should return promotions within the specified date range"""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=10)
        promotion = PromotionFactory(start_date=start_date, end_date=end_date)
        promotion.create()

        found_promotions = Promotion.find_by_date_range(start_date, end_date)
        self.assertEqual(len(found_promotions), 1)
        self.assertTrue(
            found_promotions[0].start_date >= start_date
            and found_promotions[0].end_date <= end_date
        )

    def test_find_by_date_range_no_results(self):
        """It should return no promotions if none exist within the specified date range"""
        outside_range_start = datetime.now() - timedelta(days=30)
        outside_range_end = datetime.now() - timedelta(days=20)
        PromotionFactory(
            start_date=outside_range_start, end_date=outside_range_end
        ).create()

        start_date = datetime.now()
        end_date = datetime.now() + timedelta(days=10)
        found_promotions = Promotion.find_by_date_range(start_date, end_date)
        self.assertEqual(len(found_promotions), 0)

    def test_find_by_active_status_active(self):
        """It should return only active promotions"""
        promotion1 = PromotionFactory(active_status=True)
        promotion2 = PromotionFactory(active_status=False)
        promotion1.create()
        promotion2.create()

        active_promotions = Promotion.find_by_active_status(True)
        self.assertEqual(len(active_promotions), 1)
        self.assertTrue(active_promotions[0].active_status)

    def test_find_by_active_status_inactive(self):
        """It should return only inactive promotions"""
        promotion1 = PromotionFactory(active_status=False)
        promotion1.create()

        inactive_promotions = Promotion.find_by_active_status(False)
        self.assertEqual(len(inactive_promotions), 1)
        self.assertFalse(inactive_promotions[0].active_status)

    def test_find_by_creator(self):
        """It should find promotions created by a specified user."""
        creator_id_1 = uuid4()
        creator_id_2 = uuid4()

        PromotionFactory(
            created_by=creator_id_1,
        ).create()
        PromotionFactory(
            created_by=creator_id_1,
        ).create()

        PromotionFactory(
            created_by=creator_id_2,
        ).create()

        found_promotions = Promotion.find_by_creator(creator_id_1)
        self.assertEqual(len(found_promotions), 2)
        self.assertTrue(
            all(promo.created_by == creator_id_1 for promo in found_promotions)
        )

    def test_find_by_creator_no_matches(self):
        """It should return an empty list if no promotions are created by the non-existent user."""
        non_existent_id = uuid4()

        PromotionFactory(created_by=uuid4()).create()  # Different user

        found_promotions = Promotion.find_by_creator(non_existent_id)
        self.assertEqual(len(found_promotions), 0)

    def test_find_by_updater(self):
        """It should find promotions last updated by a specified user."""
        updater_id_1 = uuid4()
        updater_id_2 = uuid4()

        PromotionFactory(
            updated_by=updater_id_1,
        ).create()
        PromotionFactory(
            updated_by=updater_id_1,
        ).create()

        PromotionFactory(
            updated_by=updater_id_2,
        ).create()

        found_promotions = Promotion.find_by_updater(updater_id_1)
        self.assertEqual(len(found_promotions), 2)
        self.assertTrue(
            all(promo.updated_by == updater_id_1 for promo in found_promotions)
        )

    def test_find_by_updater_no_matches(self):
        """It should return an empty list if no promotions are updated by the non-existent user."""
        non_existent_id = uuid4()

        PromotionFactory(updated_by=uuid4()).create()  # Different user

        found_promotions = Promotion.find_by_updater(non_existent_id)
        self.assertEqual(len(found_promotions), 0)
