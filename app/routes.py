from app import app, supabase
from app.models import *
from flask import jsonify, request


from .modules.top_stories.top_stories import get_top_stories
from .modules.search.search import (
    search_stories,
    search_articles,
)
from .security import api_required, log_request
from .exceptions import BadRequestException

from .utils.timer import Timer

perf_timer = Timer()

API_KEY_ERROR = {
    "status": "error",
    "message": "API key is incorrect or missing",
    "code": 401,
}

BAD_REQUEST_ERROR = {
    "status": "error",
    "message": "Incorrect or misconfigured parameter",
    "code": 400,
}


def get_user_data(api_key):
    data = (
        supabase.table("profile")
        .select("id", "api_key", "plan_name")
        .eq("api_key", api_key)
        .execute()
    )

    return data[0][0] or None


def authorize_api_key(key, user_data):
    """
    Check to make sure api key is valid
    """

    if app.config["REQUIRE_API_KEY"]:
        if not key or not user_data:
            return False

    return True


def verify_page_size(page_size, user_data):
    plan_name = user_data["plan_name"]

    if plan_name == "Basic":
        if page_size > 10:
            return False
    else:
        if page_size > 100:
            return False

    return True


def make_request(user_id, type):
    """
    Add the request to the users total requests
    """

    data = (
        supabase.table("requests").insert({"user_id": user_id, "type": type}).execute()
    )


# home endpoint
@app.route("/api/1")
def index():
    return """
           <h3>Newslink API </h3>
           <h4>V1.0</h4>
           """


# /top endpoint
@app.route("/api/1/top-stories")
@api_required
@log_request("top_stories")
def top():
    """
    Top stories endpoint

    params:
    - q
    - category
    - page
    - pageSize
    """

    apiKey = request.args.get("apiKey")
    category = request.args.get("category")
    q = request.args.get("q")
    page = request.args.get("page", default=0, type=int)
    pageSize = request.args.get("pageSize", default=10, type=int)

    stories = get_top_stories(category, q, page, pageSize)
    return jsonify({"status": "ok", "numResults": len(stories), "results": stories})


# /search endpoint
@app.route("/api/1/search/")
@api_required
@log_request("search")
def search():
    """
    Search endpoint

    params:
    required:
    - q
    - qInTitle

    - from
    - to
    - sources
    - sortBy
    - groupBy

    - page
    - pageSize
    """

    q = request.args.get("q")
    category = request.args.get("category")

    dateFrom = request.args.get("dateFrom")
    dateTo = request.args.get("dateTo")
    sortBy = request.args.get("sortBy")
    resType = request.args.get("resType", default="story")

    page = request.args.get("page", default=0, type=int)
    pageSize = request.args.get("pageSize", default=10, type=int)

    # if resType == "article":
    try:
        if resType == "article":
            results = search_articles(q, category, dateFrom, dateTo, sortBy)
        elif resType == "story":
            results = search_stories(q, category, dateFrom, dateTo, sortBy)
    except BadRequestException as e:
        return {
            "status": "error",
            "message": "Bad Request. " + str(e),
            "code": 400,
        }, 400

    return jsonify(
        {
            "status": "ok",
            "totalResults": len(results),
            "results": [
                r.serialize() for r in results[page * pageSize : (page + 1) * pageSize]
            ],
        }
    )
