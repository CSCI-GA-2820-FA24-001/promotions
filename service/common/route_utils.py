# import uuid
from flask import current_app as app  # Import Flask application
from datetime import datetime
from dateutil.parser import parse, ParserError


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def parse_with_try(date: str | None) -> datetime | None:
    """parse datetime string with try catch, return None if not valid"""
    try:
        if date:
            return parse(date)
    except ParserError:
        # Invalid date format, should do nothing
        app.logger.error(
            "Invalid Date Format: %s",
            date,
        )
    return None


# ######################################################################
# # Checks whether a string is uuid4 string.
# ######################################################################
# def is_uuid4(uuid_string: str) -> bool:
#     """Check if a string is a valid UUID4"""
#     try:
#         # Try to convert the string to a UUID
#         val = uuid.UUID(uuid_string, version=4)
#     except ValueError:
#         # If it's a ValueError, then it's not a valid UUID
#         return False

#     # Check if the UUID is version 4
#     return val.version == 4
