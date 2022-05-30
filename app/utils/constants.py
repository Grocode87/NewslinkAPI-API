from ..exceptions import BadRequestException

# Map the proper API category options to the ones in the DB
CATEGORY_MAP = {
    "all": None,
    "world": "World ",
    "us": "U.S. ",
    "tech": "Technology ",
    "business": "Business ",
    "science": "Science ",
    "sports": "Sports ",
    "entertainment": "Entertainment ",
}


def map_category_to_db(category):
    if category in CATEGORY_MAP:
        return CATEGORY_MAP[category]
    else:
        raise BadRequestException(
            "Invalid category parameter. Allowed: "
            + ", ".join([c for c in CATEGORY_MAP])
        )
