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
from .utils.constants import CATEGORY_MAP

perf_timer = Timer()


# home endpoint
@app.route("/api/1")
def index():
    return """
           <h3>Newslink API </h3>
           <h4>V1.0.0</h4>
           """


# /top endpoint
@app.route("/api/1/top-stories")
@api_required
@log_request("top_stories")
def top():
    """
    Top stories endpoint
    """

    category = request.args.get("category")
    q = request.args.get("q")
    page = request.args.get("page", default=0, type=int)
    pageSize = request.args.get("pageSize", default=10, type=int)

    try:
        results = get_top_stories(category, q)
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


# /search endpoint
@app.route("/api/1/search")
@api_required
@log_request("search")
def search():

    q = request.args.get("q")
    category = request.args.get("category")

    dateFrom = request.args.get("dateFrom")
    dateTo = request.args.get("dateTo")
    sortBy = request.args.get("sortBy")
    resType = request.args.get("resType", default="story")

    page = request.args.get("page", default=0, type=int)
    pageSize = request.args.get("pageSize", default=10, type=int)

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
