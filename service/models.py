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
