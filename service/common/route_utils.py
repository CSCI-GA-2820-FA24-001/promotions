# import uuid
from flask import request, abort
from flask import current_app as app  # Import Flask application
from service.common import status  # HTTP Status Codes


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


######################################################################
# Checks the ContentType of a request (same function as prof's example)
######################################################################
def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if request.headers.get("Content-Type", "") == content_type:
        return

    app.logger.error(
        "Invalid Content-Type: %s",
        request.headers.get("Content-Type", "Content-Type not set"),
    )
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


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
