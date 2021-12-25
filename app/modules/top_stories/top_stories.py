from ...models import Article, Cluster


def get_top_stories(category, q, page, pageSize):
    print(category)

    query = Cluster.query
    if category:
        query = query.filter(Cluster.category == category)

    if q:
        query = query.filter(Cluster.articles.any(Article.title.like("%" + q + "%")))

    query = query.order_by(Cluster.rank.desc())
    query = query.limit((page * pageSize) + pageSize)

    clusters = query.all()[page * pageSize :]

    return [c.serialize() for c in clusters]