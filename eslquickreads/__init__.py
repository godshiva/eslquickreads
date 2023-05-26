from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail


app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = 'harish7634ydgwid78r3re48ryf78wrc7e8rcdc'


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/eslquickreads'

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
