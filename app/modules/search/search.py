from ...models import Article, Cluster, ClusterArticle

from sqlalchemy import or_
from datetime import datetime
from dateutil import parser


def search_articles(q, qInTitle, dateFrom, dateTo, sortBy, page, pageSize):
    query = Article.query

    if q:
        query = query.filter(
            or_(
                Article.title.like("%" + q + "%"),
                Article.description.like("%" + q + "%"),
            )
        )

    elif qInTitle:
        query = query.filter(Article.title.like("%" + qInTitle + "%"))

    # try parsing dateFrom and dateTo strings, return error if fail
    if dateFrom:
        try:
            dateFrom = parser.parse(dateFrom)
            query = query.filter(Article.date_created > dateFrom)
        except:
            return {
                "status": "error",
                "message": "dateFrom is in an invalid format, please use (YYYY-MM-DD HH:MM:SS)",
            }
    if dateTo:
        try:
            dateTo = parser.parse(dateTo)
            query = query.filter(Article.date_created < dateTo)
        except:
            return {
                "status": "error",
                "message": "dateTo is in an invalid format, please use (YYYY-MM-DD HH:MM:SS)",
            }

    if sortBy == "Oldest":
        query = query.order_by(Article.date_created.asc())
    else:  # sortBy == "Newest"
        query = query.order_by(Article.date_created.desc())

    query = query.limit((page * pageSize) + pageSize)
    articles = query.all()[page * pageSize :]

    return [a.serialize() for a in articles]


def search_stories(q, qInTitle, dateFrom, dateTo, sortBy, page, pageSize):
    """
    params:

    q: keyword or phrase to look for in article title and body
    qInTitle: keyword or phrase to look for only in article titles
    dateFrom: A date and optional time for the oldest article allowed. In ISO 8601 format (e.g. 2021-12-25 or 2021-12-25T04:21:35)
    dateTo: A date and optional time for the newest article allowed. In ISO 8601 format (e.g. 2021-12-25 or 2021-12-25T04:21:35)

    sortBy:
        the order to sort the results in, options are
        Newest (default) : newest articles/stories come first
        Oldest: oldest articles/stories come first
        Relevency: articles most closely matching q come first

    page: the page of results (for pagination, make sure to use it with dateTo) (default: 0)
    pageSize: number of results per page (default: 10)

    """
    query = Cluster.query

    if q:
        query = query.filter(
            or_(
                Cluster.articles.any(Article.title.like("%" + q + "%")),
                Cluster.articles.any(Article.description.like("%" + q + "%")),
            )
        )

    elif qInTitle:
        query = query.filter(
            Cluster.articles.any(Article.title.like("%" + qInTitle + "%"))
        )

    # try parsing dateFrom and dateTo strings, return error if fail
    if dateFrom:
        try:
            dateFrom = parser.parse(dateFrom)
            query = query.filter(Cluster.last_updated > dateFrom)
        except:
            return {
                "status": "error",
                "message": "dateFrom is in an invalid format, please use (YYYY-MM-DD HH:MM:SS)",
            }
    if dateTo:
        try:
            dateTo = parser.parse(dateTo)
            query = query.filter(Cluster.last_updated < dateTo)
        except:
            return {
                "status": "error",
                "message": "dateTo is in an invalid format, please use (YYYY-MM-DD HH:MM:SS)",
            }

    if sortBy == "Oldest":
        query = query.order_by(Cluster.last_updated.asc())
    else:  # sortBy == "Newest"
        query = query.order_by(Cluster.last_updated.desc())

    query = query.limit((page * pageSize) + pageSize)
    clusters = query.all()[page * pageSize :]

    return [c.serialize() for c in clusters]
