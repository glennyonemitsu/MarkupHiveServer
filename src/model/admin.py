import base64
import hashlib
import json
import os

import bcrypt
from sqlalchemy.orm.exc import NoResultFound

from server_global import db


class Admin(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)

    def valid_password(self, password):
        hashed_pw = bcrypt.hashpw(password, self.password)
        match = hashed_pw == self.password
        return match
