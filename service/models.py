"""
Models for Promotion

All of the models are stored in this module
"""

import logging
import uuid
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, JSONB  # Import JSONB for PostgreSQL


logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Promotion(db.Model):
    """
    Represents a promotion for products, including details like name, start and end dates,
    and additional metadata.

    Attributes:
        id (UUID, required): A unique identifier for the promotion, generated automatically as a UUID.
        product_ids (JSONB, optional): A list of product IDs associated with the promotion, stored as a JSON array.
        name (str, required): The name of the promotion.
        description (str, optional): A detailed description of the promotion.
        start_date (datetime, required): The start date and time of the promotion.
        end_date (datetime, required): The end date and time of the promotion.
        active_status (bool, required): A boolean indicating whether the promotion is active.
        created_by (UUID, required): The UUID of the user who created the promotion.
        updated_by (UUID, required): The UUID of the user who last updated the promotion.
        created_at (datetime, required): The timestamp when the promotion was created, default set to the current UTC time.
        updated_at (datetime, required): The timestamp when the promotion was last updated.
        extra (JSONB, optional): Additional metadata for the promotion, stored as a JSON object.
    """

    ##################################################
    # Table Schema
    ##################################################

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_ids = db.Column(JSONB, nullable=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    active_status = db.Column(db.Boolean, nullable=False)
    created_by = db.Column(UUID(as_uuid=True), nullable=False)
    updated_by = db.Column(UUID(as_uuid=True), nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    extra = db.Column(JSONB)

    def __repr__(self):
        return f"<Promotion {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Promotion to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Promotion to the database
        """
        logger.info("Saving %s", self.name)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Promotion from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Promotion into a dictionary"""
        return {
            "id": str(self.id),  # UUID to string
            "product_ids": self.product_ids,
            "name": self.name,
            "description": self.description,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "active_status": self.active_status,
            "created_by": str(self.created_by),
            "updated_by": str(self.updated_by),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "extra": self.extra,
        }

    def deserialize(self, data):
        """
        Deserializes a Promotion from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.start_date = datetime.fromisoformat(data["start_date"])
            self.end_date = datetime.fromisoformat(data["end_date"])
            self.active_status = data["active_status"]
            self.created_by = uuid.UUID(data["created_by"])  # Convert string to UUID
            self.updated_by = uuid.UUID(data["updated_by"])  # Convert string to UUID

            # Optional fields (use `.get()` to avoid KeyError if not present)
            self.product_ids = data.get("product_ids")
            self.description = data.get("description")
            self.extra = data.get("extra")

        # AttributeError is unlikely in the current implementation
        # but might be needed in future if attribute access or method calls are added.
        # except AttributeError as error:
        #     raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Promotion: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Promotion: body of request contained bad or no data "
                + str(error)
            ) from error
        except ValueError as error:
            raise DataValidationError(
                "Invalid Promotion: body of request contained bad data type "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Promotions in the database"""
        logger.info("Processing all Promotions")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Promotion by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Promotions with the given name

        Args:
            name (string): the name of the Promotions you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_product_id(cls, product_id: str) -> list:
        """
        Returns all promotions that include the given product ID.

        Args:
            product_id (product_id): The product ID to match within the promotion's product_ids
        """
        logger.info("Processing product ID query for %s ...", product_id)
        return cls.query.filter(cls.product_ids.contains([product_id])).all()

    @classmethod
    def find_by_start_date(
        cls, start_date: datetime, exact_match: bool = False
    ) -> list:
        """
        Returns promotions based on the start date. The behavior changes based on the `exact_match` flag.

        Args:
            start_date (datetime): The date to match against the promotion's start date.
            exact_match (bool, optional): Determines if the search should return promotions
                that start exactly on `start_date` (True) or on and after `start_date` (False).
                Default is False.
        """
        logger.info(
            "Processing start date query for promotions starting %s %s ...",
            "exactly on" if exact_match else "on or after",
            start_date,
        )
        if exact_match:
            return cls.query.filter(cls.start_date == start_date).all()

        return cls.query.filter(cls.start_date >= start_date).all()

    @classmethod
    def find_by_end_date(cls, end_date: datetime, exact_match: bool = False) -> list:
        """
        Returns promotions based on the end date. The behavior changes based on the `exact_match` flag.

        Args:
            end_date (datetime): The date to match against the promotion's end date.
            exact_match (bool, optional): Determines if the search should return promotions that
                end exactly on `end_date` (True) or on or before `end_date` (False).
                Default is False.
        """
        logger.info(
            "Processing end date query for promotions ending %s %s ...",
            "exactly on" if exact_match else "on or before",
            end_date,
        )
        if exact_match:
            return cls.query.filter(cls.end_date == end_date).all()

        return cls.query.filter(cls.end_date <= end_date).all()

    @classmethod
    def find_by_date_range(cls, start_date: datetime, end_date: datetime) -> list:
        """
        Returns all promotions within a specified date range.

        Args:
            start_date (datetime): the start of the date range
            end_date (datetime) : the end of the date range
        """
        logger.info(
            "Processing date range query from %s to %s ...", start_date, end_date
        )
        return cls.query.filter(
            cls.start_date <= end_date, cls.end_date >= start_date
        ).all()

    @classmethod
    def find_by_active_status(cls, active_status: bool) -> list:
        """Returns all promotions by their active status.
        Args:
            active_status (boolean): True for active promotions, False otherwise
        """
        logger.info(
            "Processing active status query for active_status=%s ...", active_status
        )
        return cls.query.filter(cls.active_status == active_status).all()

    @classmethod
    def find_by_creator(cls, user_id: uuid.UUID) -> list:
        """
        Returns all promotions created by a specific user.

        Args:
            user_id (UUID): The UUID of the user who created the promotions
        """
        logger.info("Processing creator query for user_id=%s ...", user_id)
        return cls.query.filter(cls.created_by == user_id).all()

    @classmethod
    def find_by_updater(cls, user_id: uuid.UUID) -> list:
        """
        Returns all promotions last updated by a specific user.

        Args:
            user_id (UUID): The UUID of the user who last updated the promotions
        """
        logger.info("Processing updater query for user_id=%s ...", user_id)
        return cls.query.filter(cls.updated_by == user_id).all()
