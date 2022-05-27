import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "my_precious_secret_key")
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 7200
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "mysql://{0}:{1}@{2}/{3}".format(
        "root", "Hunter1?23", "localhost", "newsapp"
    )
    REQUIRE_API_KEY = True
    SUPABASE_URL = "https://rltpyqhebpfhfmbwaeoj.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiIsImlhdCI6MTYzNzYzMzUwMywiZXhwIjoxOTUzMjA5NTAzfQ.qCm7EeAuAqzz4cgdMD-ncrgzccslH78xSTpmE8-JQeo"


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "mysql://{0}:{1}@{2}/{3}".format(
        "root", "Hunter1?23", "localhost", "newsapp"
    )
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REQUIRE_API_KEY = False


class ProductionConfig(Config):
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = "mysql://{0}:{1}@{2}/{3}".format(
        "root", "Hunter1?23", "localhost:3306", "news"
    )

    REQUIRE_API_KEY = True
    SUPABASE_URL = "https://rltpyqhebpfhfmbwaeoj.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiIsImlhdCI6MTYzNzYzMzUwMywiZXhwIjoxOTUzMjA5NTAzfQ.qCm7EeAuAqzz4cgdMD-ncrgzccslH78xSTpmE8-JQeo"


config_by_name = dict(dev=DevelopmentConfig, test=TestingConfig, prod=ProductionConfig)

key = Config.SECRET_KEY
