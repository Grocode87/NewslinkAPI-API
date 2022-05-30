from ...models import Article, Cluster, ClusterArticle

from sqlalchemy import or_
from datetime import datetime
from dateutil import parser
from .advanced_search_parser import get_sqlalch_filter_query

from ...exceptions import BadRequestException
from ...utils.constants import map_category_to_db


def get_date(date_string):
    try:
        parser.parse(date_string)
    except:
        raise BadRequestException(
            "Date is in an invalid format, please use ISO 8601 format (e.g. 2022-05-23 or 2022-05-23T01:45:56)"
        )


def search_articles(q, category, dateFrom, dateTo, sortBy):
    query = Article.query

    # P1: query filters
    if q:
        query = query.filter(get_sqlalch_filter_query(q))
    if category:
        query = query.filter(Article.category == map_category_to_db(category))

    # P2: date filters
    if dateFrom:
        date_from = get_date(dateFrom)
        query = query.filter(Article.date_created >= date_from)

    if dateTo:
        date_to = get_date(dateTo)
        query = query.filter(Article.date_created <= date_to)

    # P3: sorting by sortBy
    if sortBy == "oldest":
        query = query.order_by(Article.date_created.asc())
    elif sortBy == "newest":
        query = query.order_by(Article.date_created.desc())

    # NOT IMPLEMENTED, NEED TO CREATE A SYSTEM THAT COUNTS QUERY MATCHES
    elif sortBy == "relevance":
        query = query.order_by(Article.date_created.desc())

    # NOT IMPLEMENTED, NEED METRIC TO DETERMINE ARTICLE's STORY POPULARITY
    elif sortBy == "popularity":
        query = query.order_by(Article.date_created.desc())

    elif not sortBy:  # default: newest
        query = query.order_by(Article.date_created.desc())
    else:
        raise BadRequestException("Invalid sortBy parameter")

    results = query.all()

    return results


def search_stories(q, category, dateFrom, dateTo, sortBy):
    query = Cluster.query

    # P1: query filters
    if q:

        def filter_param(query):
            return Cluster.articles.any(Article.title.like(query))

        query = query.filter(get_sqlalch_filter_query(q, cluster=True))

    if category:
        query = query.filter(Cluster.category == map_category_to_db(category))

    # P2: date filters
    if dateFrom:
        date_from = get_date(dateFrom)
        query = query.filter(Cluster.last_updated >= date_from)

    if dateTo:
        date_to = get_date(dateTo)
        query = query.filter(Cluster.last_updated <= date_to)

    # P3: sorting by sortBy
    if sortBy == "oldest":
        query = query.order_by(Cluster.last_updated.asc())
    elif sortBy == "newest":
        query = query.order_by(Cluster.last_updated.desc())

    # NOT IMPLEMENTED, NEED TO CREATE A SYSTEM THAT COUNTS QUERY MATCHES
    elif sortBy == "relevance":
        query = query.order_by(Cluster.last_updated.desc())

    elif sortBy == "popularity":
        query = query.order_by(Cluster.rank.desc())

    elif not sortBy:  # default: newest
        query = query.order_by(Cluster.last_updated.desc())
    else:
        raise BadRequestException("Invalid sortBy parameter")

    results = query.all()

    return results