from app import app, db
from .utils.timer import Timer

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref
from sqlalchemy import and_

import random

from collections import Counter

Base = declarative_base()
metadata = Base.metadata

db.reflect()


class Article(db.Model):
    __tablename__ = "article"

    entities = db.relationship("Entity", secondary="article_entity", viewonly=True)

    def serialize(self):
        timer = Timer()

        ## TODO: FIGURE OUT TOP ENTITIES EFFICIENTLY

        top_entities = (
            Entity.query.join(ArticleEntity, Entity.id == ArticleEntity.entity_id)
            .add_columns(ArticleEntity.score)
            .filter(ArticleEntity.article_id == self.id)
            .order_by(ArticleEntity.score.desc())
            .limit(3)
            .all()
        )

        top_entities = [e[0].serialize() for e in top_entities]

        return {
            "type": "article",
            "title": self.title,
            "description": self.description,
            "source": self.source,
            "url": self.url,
            "urlToImage": self.image_url,
            "topEntities": top_entities[:5],
            "sentiment": 0,
            "dateCreated": self.date_created,
        }


class Cluster(db.Model):
    __tablename__ = "cluster"

    articles = db.relationship("Article", secondary="cluster_article", viewonly=True)

    def serialize(self):
        top_article = None
        all_articles = []

        story_entities = (
            ArticleEntity.query.join(Entity)
            .with_entities(Entity, ArticleEntity.score)
            .filter(ArticleEntity.article_id.in_([a.id for a in self.articles]))
            .all()
        )

        entity_scores = {}
        for entity in story_entities:
            if entity[0] in entity_scores:
                entity_scores[entity[0]] += entity[1]
            else:
                entity_scores[entity[0]] = entity[1]

        entity_scores = sorted(entity_scores.items(), key=lambda x: x[1], reverse=True)

        entities = [e[0].serialize() for e in entity_scores[:3]]

        for a in self.articles:
            if a.id == self.top_article_id:
                top_article = a.serialize()
            else:
                all_articles.append(a.serialize())

        return {
            "type": "story",
            "topArticle": top_article,
            "articles": all_articles,
            "category": self.category,
            "dateCreated": self.date_created,
            "sentiment": 0,
            "topEntities": entities,
        }


class Entity(db.Model):
    __tablename__ = "entity"

    def serialize(self, score=None):
        return self.name
        # return {
        #    "name": self.name,
        #    "score": score,
        # }


class ClusterArticle(db.Model):
    __tablename__ = "cluster_article"

    cluster = db.relationship(Cluster, backref=backref("cluster_article"))
    article = db.relationship(Article, backref=backref("cluster_article"))


class ArticleEntity(db.Model):
    __tablename__ = "article_entity"

    article = db.relationship(Article, backref=backref("article_entity"))
    entity = db.relationship(Entity, backref=backref("article_entity"))


class EntityFrequency(db.Model):
    __tablename__ = "entity_frequency"

    entity = db.relationship(Entity)
