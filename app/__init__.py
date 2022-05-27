from .config import config_by_name

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask import Flask
from flask_caching import Cache

from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()  # take environment variables from .env.

app = Flask(__name__)

print(os.getenv("CONFIG_NAME", "prod"))
CORS(app)
app.config.from_object(config_by_name[os.getenv("CONFIG_NAME", "prod")])


db = SQLAlchemy(app)
migrate = Migrate(app, db)

supabase = None
if app.config["REQUIRE_API_KEY"]:
    supabase = create_client(app.config["SUPABASE_URL"], app.config["SUPABASE_KEY"])

from . import routes, models
