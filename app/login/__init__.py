from flask import Blueprint

loginbp = Blueprint('login', __name__,url_prefix='/login')

from . import login