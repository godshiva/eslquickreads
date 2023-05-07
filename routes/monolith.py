from flask import Flask, render_template, redirect, url_for, flash, request, session, Response
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
import json
import os
import re
import hashlib
import secrets
import mailtrap as mt
import random


if __name__ == '__main__':
    #app = Flask(__name__)
    pass  # figure out how to split into pieces


