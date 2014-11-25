__author__ = 'wan'
from flask import render_template


class Validate():
    def __init__(self, db, session):
        self.db = db
        self.session = session

    def is_login(self):
        if '_user' in self.session:
            return True
        return False