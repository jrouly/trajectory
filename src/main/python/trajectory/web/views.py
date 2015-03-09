from flask import Blueprint

mod = Blueprint('web', __name__, url_prefix='/')

@mod.route('', methods=['GET'])
def dashboard():
    return "Hello, world."
