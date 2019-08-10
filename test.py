import unittest
import re

from flask_pymongo import PyMongo

import app as app_module

app = app_module.app

# Setting up test DB on Mongo and switching CSRF checks off
app.config["TESTING"] = True
app.config["WTF_CSRF_ENABLED"] = False
app.config['MONGO_URI'] = 'mongodb://localhost:27017/JusteatTesting'

mongo = PyMongo(app)
app_module.mongo = mongo


class AppTestCase(unittest.TestCase):
    """Clean the DB"""

    def setUp(self):
        self.client = app.test_client()
        with app.app_context():
            mongo.db.users.delete_many({})
            mongo.db.Recipes.delete_many({})


class AppTests(AppTestCase):
    """Check if Home page is loading"""

    def test_index(self):
        res = self.client.get('/')
        data = res.data.decode('utf-8')
        assert res.status == '200 OK'
        assert 'Eat_IT' in data

    """ Check if getRecipes is loading"""

    def test_getRecipes(self):
        res = self.client.get('/recipes')
        data = res.data.decode('utf-8')
        assert res.status == '200 OK'
        assert 'Filter' in data
