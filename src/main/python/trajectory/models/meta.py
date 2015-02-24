"""
trajectory/models/meta.py
Author: Jean Michel Rouly

Define references to the database meta objects to allow reference on a
global scale.
"""


from trajectory import constants as TRJ
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


Engine = create_engine(TRJ.DATABASE_URI)
Base = declarative_base()
Session = sessionmaker(bind=Engine)
