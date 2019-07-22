from flask import Flask, render_template, request, url_for, redirect
import os
from flask_pymongo import PyMongo
from bson.objectid import ObjectId


app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'task_manager'
app.config["MONGO_URI"] = os.environ.get('MONGO_URI')


mongo = PyMongo(app)


@app.route('/')
@app.route('/index')
def index():
    return render_template('base.html')


@app.route('/recipes')
def get_recipes():
    return render_template('recipes.html', recipe=mongo.db.Recipes.find())


@app.route('/add_recipe')
def add_recipe():
    return render_template('addrecipe.html', skill=mongo.db.skill.find(), orgin=mongo.db.cusine.find())


@app.route('/insert_recipe', methods=['POST'])
def insert_recipe():
    tasks = mongo.db.Recipes
    tasks.insert_one(request.form.to_dict())
    return redirect(url_for('get_recipes'))


@app.route('/single/<recipe_id>')
def recipe_info(recipe_id):
    recipe = mongo.db.Recipes.find_one({'_id': ObjectId(recipe_id)})
    return render_template('recipeInfo.html', recipeInfo=recipe)


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'), port=os.environ.get('PORT'), debug=True)
