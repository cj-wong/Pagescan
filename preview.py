from flask import Blueprint


preview = Blueprint('Previews', __name__, static_folder='previews')
