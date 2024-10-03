"""
Test Factory to make fake objects for testing
"""

from datetime import timedelta, timezone
import factory
from service.models import Promotion

PROMOTION_DURATION_DAYS = 30


class PromotionFactory(factory.Factory):
    """Creates fake pets that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Promotion

    id = factory.Faker("uuid4")
    product_ids = factory.List([factory.Faker("uuid4") for _ in range(3)])
    name = factory.Faker("word")
    description = factory.Faker("sentence")
    start_date = factory.Faker("date_time_this_decade", tzinfo=timezone.utc)
    end_date = factory.LazyAttribute(
        lambda obj: obj.start_date + timedelta(days=PROMOTION_DURATION_DAYS)
    )
    active_status = factory.Faker("boolean")
    created_by = factory.Faker("uuid4")
    updated_by = factory.Faker("uuid4")
    created_at = factory.Faker("date_time_this_year", tzinfo=timezone.utc)
    updated_at = factory.Faker("date_time_this_year", tzinfo=timezone.utc)
    extra = {
        "promotion_type": "description",
        "value": None,
    }
