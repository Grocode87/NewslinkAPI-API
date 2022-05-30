from ...models import Article, Cluster
from ..search.advanced_search_parser import get_sqlalch_filter_query
from ...utils.constants import map_category_to_db


def get_top_stories(category, q):

    query = Cluster.query

    if category:
        query = query.filter(Cluster.category == map_category_to_db(category))

    if q:
        query = query.filter(get_sqlalch_filter_query(q, cluster=True))

    query = query.order_by(Cluster.rank.desc())

    query = query.limit(100)

    results = query.all()

    return results