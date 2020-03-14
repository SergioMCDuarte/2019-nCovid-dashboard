from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_restful import Resource, Api

app = Flask(__name__)

from website.core.views import core
from website.country_details.views import country_details
from website.world.views import world
from website.china_evolution.views import china_evolution

app.register_blueprint(core)
app.register_blueprint(country_details)
app.register_blueprint(world)
app.register_blueprint(china_evolution)
