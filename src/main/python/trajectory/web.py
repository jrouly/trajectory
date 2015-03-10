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


# Manage error handling.
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# Define routing for dashboard page.
@app.route('/')
def dashboard():
    return "Dashboard."

# Define routing for university list.
@app.route('/universities/')
def university_list():
    return "University list."

# Define routing for university index pages.
@app.route('/universities/<string:university_abbr>/')
def university(university_abbr=None):
    return "University: %s" % university_abbr

# Define routing for departmental pages.
@app.route('/universities/<string:university_abbr>/<string:dept_abbr>/')
def department(university_abbr=None, dept_abbr=None):
    return "Uni %s Dept %s" % (university_abbr, dept_abbr)

# Define routing for topic list.
@app.route('/topics/')
def topics():
    return "Topics."

# Define routing for about page.
@app.route('/about/')
def about():
    return render_template("about.html")
