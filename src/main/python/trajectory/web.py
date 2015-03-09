from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from jinja2 import FileSystemLoader
from trajectory import config as TRJ

app = Flask(__name__)
app.config.from_object(dict(
    DEBUG = True,
    SQLALCHEMY_DATABASE_URI = TRJ.DATABASE_URI,
    THREADS_PER_PAGE = 8,
))
app.jinja_loader = FileSystemLoader(TRJ.TEMPLATES)
app.db = SQLAlchemy(app)


# Define routing.
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.route('/', methods=['GET'])
def dashboard():
    return "Hello, world."


if __name__ == '__main__':
    app.run()
