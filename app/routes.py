from app import app, supabase
from app.models import *
from flask import jsonify, request

from .modules.top_stories.top_stories import get_top_stories
from .modules.search.search import search_stories, search_articles


from .utils.timer import Timer

perf_timer = Timer()


def authorize_api_key(key, request_type):
    """
    Check to make sure api key is valid
    """
    key_error = {"status": "error", "message": "API key is incorrect or missing"}

    if app.config["REQUIRE_API_KEY"]:
        if not key:
            return key_error

        data = (
            supabase.table("profile")
            .select("id", "api_key")
            .eq("api_key", key)
            .execute()
        )
        if len(data.get("data")) > 0:
            user_id = data.get("data")[0]["id"]
            make_request(user_id, request_type)
            return None
        else:
            return key_error
    else:
        return None


def make_request(user_id, type):
    """
    Add the request to the users total requests
    """

    data = (
        supabase.table("requests").insert({"user_id": user_id, "type": type}).execute()
    )

    assert data.get("status_code") in (200, 201)


# home endpoint
@app.route("/")
def index():
    return """
           <h3>Newslink API </h3>
           <h4>V1.0</h4>
           """


# /top endpoint
@app.route("/top-stories")
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

    key_auth_msg = authorize_api_key(
        apiKey, {"type": "top stories", "num_requests": pageSize}
    )

    if key_auth_msg:
        return key_auth_msg

    stories = get_top_stories(category, q, page, pageSize)
    return jsonify({"status": "ok", "numResults": len(stories), "results": stories})


# /search endpoint
@app.route("/search/")
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
    apiKey = request.args.get("apiKey")
    q = request.args.get("q")
    qInTitle = request.args.get("qInTitle")

    dateFrom = request.args.get("from")
    dateTo = request.args.get("to")
    sortBy = request.args.get("sortBy")
    resultType = request.args.get("resultType", default="story")

    page = request.args.get("page", default=0, type=int)
    pageSize = request.args.get("pageSize", default=10, type=int)

    key_auth_msg = authorize_api_key(apiKey, {"type": "", "num_requests": pageSize})

    if key_auth_msg:
        return key_auth_msg

    if resultType == "article":
        stories = search_articles(q, qInTitle, dateFrom, dateTo, sortBy, page, pageSize)
    elif resultType == "story":
        stories = search_stories(q, qInTitle, dateFrom, dateTo, sortBy, page, pageSize)
    else:
        return jsonify({"status": "error", "message": "Incorrect result type"})
    if type(stories) == list:
        return jsonify({"status": "ok", "numResults": len(stories), "results": stories})
    else:
        return stories
