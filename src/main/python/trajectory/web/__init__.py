from flask import Flask

app = Flask(__name__)
# app.config. ...

from web.views import mod as webModule
app.register_blueprint(webModule)
