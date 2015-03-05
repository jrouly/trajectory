"""
trajectory/visualize.py
Author: Jean Michel Rouly

Generate a web-based visualization suite from the stored database
information.
"""


from trajectory import config as TRJ
from jinja2 import Environment, FileSystemLoader
import os


# Point the template loader to the templates directory.
env = Environment(loader=FileSystemLoader(TRJ.TEMPLATES))

template = env.get_template("index.html")
with open("/tmp/index.html", "w") as fp:
    fp.write(template.render(foo="bar"))
