from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
import json
import os

app = Flask(__name__, instance_relative_config=True)

config_file = "../configdata/debug.json"
prod_file_name = "/home/algorithmguy/mysite/configdata/prod.json"
if os.path.exists(prod_file_name):
    config_file = prod_file_name

# detect prod

working_dir = os.getcwd()
is_prod = ("/home/algorithmguy" in working_dir)

assert ("prod.json" in config_file) == is_prod, f"prod.json should not be available on non prod, and should not be missing on prod. {is_prod} {working_dir} {config_file}"

with open(config_file, "r") as f:
    config = json.load(f)

for key, value in config.items():
    app.config[key] = value

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# mail details
app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
mail = Mail(app)


# register your routes here only

from eslquickreads.route import route
from eslquickreads.errors import errors
from eslquickreads.lesson import lesson
from eslquickreads.developer import developer
